"""Regression tests for logical move counts and visual animation routes."""

from dataclasses import replace

import pytest

from ludo.app import GameFacade, LegalMoveSnapshot, MoveRouteStepSnapshot
from ludo.domain import (
    BoardTopology,
    FixedClock,
    FixedDice,
    FixedSpecialDie,
    Match,
    MovementRules,
    Piece,
    PieceState,
    Player,
    PlayerColor,
)
from ludo.domain.match import FixedColorRandomizer
from ludo.domain.movement import MoveDestinationKind, ProposedMove

ALL_COLORS = (
    PlayerColor.RED,
    PlayerColor.GREEN,
    PlayerColor.YELLOW,
    PlayerColor.BLUE,
)
CORNER_TRANSITIONS = (
    (5, 6),
    (18, 19),
    (31, 32),
    (44, 45),
)


@pytest.mark.parametrize("color", ALL_COLORS)
@pytest.mark.parametrize("progress", range(52))
@pytest.mark.parametrize("dice_value", range(1, 7))
def test_every_outer_move_route_matches_authoritative_step_count(
    color: PlayerColor, progress: int, dice_value: int
) -> None:
    piece = Piece("moving", color, PieceState.ON_OUTER_PATH, progress)
    proposal = MovementRules().propose_move(piece, dice_value)
    assert proposal is not None

    legal_move = _legal_move_for(piece, dice_value)

    assert _journey_progress(proposal) - progress == dice_value
    assert len(legal_move.route) == dice_value
    assert legal_move.route == _expected_route(color, progress, dice_value)
    assert legal_move.route[-1] == _destination_route_step(legal_move)


@pytest.mark.parametrize(("start_index", "end_index"), CORNER_TRANSITIONS)
def test_all_four_corner_transitions_are_single_route_steps(
    start_index: int, end_index: int
) -> None:
    piece = Piece("moving", PlayerColor.RED, PieceState.ON_OUTER_PATH, start_index)

    legal_move = _legal_move_for(piece, 1)

    assert len(legal_move.route) == 1
    assert legal_move.route[0].global_outer_index == end_index


def test_outer_path_wraparound_route_uses_one_step_per_square() -> None:
    topology = BoardTopology()
    start_progress = (51 - topology.start_position(PlayerColor.BLUE)) % 52
    piece = Piece("moving", PlayerColor.BLUE, PieceState.ON_OUTER_PATH, start_progress)

    legal_move = _legal_move_for(piece, 3)

    assert [step.global_outer_index for step in legal_move.route] == [0, 1, 2]


def test_hazard_route_clamps_penalty_at_start_without_wraparound() -> None:
    piece = Piece("moving", PlayerColor.RED, PieceState.ON_OUTER_PATH, 0)

    legal_move = _legal_move_for(piece, 1, hazard_positions=frozenset({1}))

    assert [step.global_outer_index for step in legal_move.route] == [1, 0]


def test_outer_to_home_path_route_remains_one_step_per_dice_value() -> None:
    piece = Piece("moving", PlayerColor.RED, PieceState.ON_OUTER_PATH, 50)

    legal_move = _legal_move_for(piece, 4)

    assert len(legal_move.route) == 4
    assert legal_move.route == (
        MoveRouteStepSnapshot(MoveDestinationKind.OUTER_PATH, global_outer_index=51),
        MoveRouteStepSnapshot(
            MoveDestinationKind.HOME_PATH,
            home_color=PlayerColor.RED,
            home_index=0,
        ),
        MoveRouteStepSnapshot(
            MoveDestinationKind.HOME_PATH,
            home_color=PlayerColor.RED,
            home_index=1,
        ),
        MoveRouteStepSnapshot(
            MoveDestinationKind.HOME_PATH,
            home_color=PlayerColor.RED,
            home_index=2,
        ),
    )


def _legal_move_for(
    piece: Piece,
    dice_value: int,
    *,
    hazard_positions: frozenset[int] = frozenset(),
) -> LegalMoveSnapshot:
    match = _match_for(piece, dice_value, hazard_positions=hazard_positions)
    facade = GameFacade.from_match(match)
    facade.roll()
    result = facade.roll_special()
    assert len(result.legal_moves) == 1
    return result.legal_moves[0]


def _match_for(
    piece: Piece,
    dice_value: int,
    *,
    hazard_positions: frozenset[int] = frozenset(),
) -> Match:
    match = Match.create(
        tuple(color.value.title() for color in ALL_COLORS),
        color_randomizer=FixedColorRandomizer(samples=[ALL_COLORS]),
        hazard_positions=hazard_positions,
        dice=FixedDice([dice_value]),
        special_die=FixedSpecialDie([0] * 20),
        clock=FixedClock(),
    )
    player = match.player_by_color(piece.owner_color)
    match.turn_engine.replace_player(
        replace(player, pieces=(piece, *_finished_pieces(piece.owner_color)))
    )
    match.turn_engine.current_player_index = _player_index(match.turn_engine.players, player.color)
    return match


def _finished_pieces(color: PlayerColor) -> tuple[Piece, ...]:
    return tuple(
        Piece(f"{color.value}-finished-{index}", color, PieceState.FINISHED)
        for index in range(3)
    )


def _player_index(players: tuple[Player, ...], color: PlayerColor) -> int:
    for index, player in enumerate(players):
        if player.color is color:
            return index
    raise AssertionError(f"Missing player for {color}.")


def _journey_progress(proposal: ProposedMove) -> int:
    moved = proposal.piece
    if moved.state is PieceState.ON_OUTER_PATH and moved.path_progress is not None:
        return moved.path_progress
    if moved.state is PieceState.ON_HOME_PATH and moved.path_progress is not None:
        return 52 + moved.path_progress
    if moved.state is PieceState.FINISHED:
        return 57
    raise AssertionError(f"Unexpected moved piece state {moved.state}.")


def _expected_route(
    color: PlayerColor, progress: int, dice_value: int
) -> tuple[MoveRouteStepSnapshot, ...]:
    return tuple(_route_step(color, progress + step) for step in range(1, dice_value + 1))


def _route_step(color: PlayerColor, journey_progress: int) -> MoveRouteStepSnapshot:
    topology = BoardTopology()
    if journey_progress < 52:
        return MoveRouteStepSnapshot(
            MoveDestinationKind.OUTER_PATH,
            global_outer_index=topology.global_outer_index(color, journey_progress),
        )
    if journey_progress < 57:
        return MoveRouteStepSnapshot(
            MoveDestinationKind.HOME_PATH,
            home_color=color,
            home_index=journey_progress - 52,
        )
    return MoveRouteStepSnapshot(MoveDestinationKind.FINISHED, home_color=color)


def _destination_route_step(legal_move: LegalMoveSnapshot) -> MoveRouteStepSnapshot:
    destination = legal_move.destination
    return MoveRouteStepSnapshot(
        destination.kind,
        global_outer_index=destination.global_outer_index,
        home_color=destination.home_color,
        home_index=destination.home_index,
    )
