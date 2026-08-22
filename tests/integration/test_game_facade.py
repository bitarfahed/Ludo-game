"""Integration tests for the application-facing game facade."""

from dataclasses import FrozenInstanceError, replace

import pytest

from ludo.app import FacadeResultKind, GameFacade, GameFacadeError
from ludo.domain import (
    FixedClock,
    FixedDice,
    Match,
    OuterPathOccupancy,
    Piece,
    PieceState,
    Player,
    PlayerColor,
    TurnPhase,
)
from ludo.domain.match import FixedColorRandomizer


def create_facade(
    rolls: list[int] | None = None,
    colors: tuple[PlayerColor, ...] = (PlayerColor.RED, PlayerColor.YELLOW),
) -> GameFacade:
    facade = GameFacade()
    opposite_pair = _opposite_pair_for(colors)
    facade.start_match(
        ("Alice", "Bob"),
        color_randomizer=FixedColorRandomizer(choices=[opposite_pair], samples=[colors]),
        dice=FixedDice(rolls or [6]),
        clock=FixedClock(),
    )
    return facade


def create_match(
    rolls: list[int],
    players: tuple[Player, ...],
    colors: tuple[PlayerColor, ...] = (PlayerColor.RED, PlayerColor.YELLOW),
) -> Match:
    opposite_pair = _opposite_pair_for(colors)
    match = Match.create(
        ("Alice", "Bob"),
        color_randomizer=FixedColorRandomizer(choices=[opposite_pair], samples=[colors]),
        dice=FixedDice(rolls),
        clock=FixedClock(),
    )
    match.turn_engine.players = players
    match.players = players
    return match


def _opposite_pair_for(colors: tuple[PlayerColor, ...]) -> tuple[PlayerColor, PlayerColor]:
    if set(colors) == {PlayerColor.RED, PlayerColor.YELLOW}:
        return (PlayerColor.RED, PlayerColor.YELLOW)
    return (PlayerColor.GREEN, PlayerColor.BLUE)


def player_with_first_piece(player_id: str, color: PlayerColor, first_piece: Piece) -> Player:
    initial = Player(id=player_id, name=player_id[:10], color=color)
    return replace(initial, pieces=(first_piece, *initial.pieces[1:]))


def outer_piece(piece_id: str, color: PlayerColor, progress: int) -> Piece:
    return Piece(
        id=piece_id,
        owner_color=color,
        state=PieceState.ON_OUTER_PATH,
        path_progress=progress,
    )


def home_piece(piece_id: str, color: PlayerColor, progress: int) -> Piece:
    return Piece(
        id=piece_id,
        owner_color=color,
        state=PieceState.ON_HOME_PATH,
        path_progress=progress,
    )


def finished_piece(piece_id: str, color: PlayerColor) -> Piece:
    return Piece(id=piece_id, owner_color=color, state=PieceState.FINISHED)


def test_match_creation_through_facade_returns_public_snapshot() -> None:
    facade = create_facade(colors=(PlayerColor.YELLOW, PlayerColor.RED))

    snapshot = facade.snapshot()

    assert snapshot.phase is TurnPhase.WAITING_FOR_ROLL
    assert [player.color for player in snapshot.players] == [PlayerColor.RED, PlayerColor.YELLOW]
    assert snapshot.inactive_colors == frozenset({PlayerColor.GREEN, PlayerColor.BLUE})
    assert not snapshot.is_complete


def test_current_player_and_phase_are_queryable() -> None:
    facade = create_facade()

    assert facade.current_player().color is PlayerColor.RED
    assert facade.current_phase() is TurnPhase.WAITING_FOR_ROLL
    assert facade.seconds_remaining() == 10


def test_valid_roll_flow_exposes_dice_and_legal_moves() -> None:
    facade = create_facade([6])

    result = facade.roll()

    assert result.kind is FacadeResultKind.DICE_ROLLED
    assert result.dice_value == 6
    assert facade.current_phase() is TurnPhase.WAITING_FOR_MOVE
    assert len(result.legal_moves) == 4
    assert {move.owner_color for move in result.legal_moves} == {PlayerColor.RED}
    assert [step.global_outer_index for step in result.legal_moves[0].route] == [0]


def test_legal_move_route_crosses_outer_to_home_boundary() -> None:
    red_piece = outer_piece("red-1", PlayerColor.RED, 50)
    match = create_match(
        [4],
        (
            player_with_first_piece("red", PlayerColor.RED, red_piece),
            Player(id="yellow", name="Yellow", color=PlayerColor.YELLOW),
        ),
    )
    facade = GameFacade.from_match(match)

    result = facade.roll()

    route = result.legal_moves[0].route
    assert route[0].global_outer_index == 51
    assert [(step.home_color, step.home_index) for step in route[1:]] == [
        (PlayerColor.RED, 0),
        (PlayerColor.RED, 1),
        (PlayerColor.RED, 2),
    ]


def test_valid_piece_selection_moves_piece_and_exposes_bonus_roll_state() -> None:
    facade = create_facade([6])

    roll_result = facade.roll()
    result = facade.choose_piece(roll_result.legal_moves[0].piece_id)

    assert result.kind is FacadeResultKind.PIECE_MOVED
    assert result.moved_piece is not None
    assert result.moved_piece.state is PieceState.ON_OUTER_PATH
    assert result.moved_piece.path_progress == 0
    assert result.bonus_available
    assert result.bonus_reasons == frozenset({"rolled_6"})
    assert facade.current_player().color is PlayerColor.RED


def test_turn_transition_is_exposed_after_non_bonus_move() -> None:
    red_piece = outer_piece("red-1", PlayerColor.RED, 0)
    match = create_match(
        [3],
        (
            player_with_first_piece("red", PlayerColor.RED, red_piece),
            Player(id="yellow", name="Yellow", color=PlayerColor.YELLOW),
        ),
    )
    facade = GameFacade.from_match(match)

    facade.roll()
    result = facade.choose_piece("red-1")

    assert result.turn_changed
    assert result.snapshot.current_player is not None
    assert result.snapshot.current_player.color is PlayerColor.YELLOW


def test_no_legal_move_result_and_notice_completion_are_exposed() -> None:
    facade = create_facade([1])

    roll_result = facade.roll()
    pass_result = facade.complete_no_legal_move_notice()

    assert roll_result.kind is FacadeResultKind.NO_LEGAL_MOVE
    assert roll_result.legal_moves == ()
    assert roll_result.snapshot.phase is TurnPhase.NO_LEGAL_MOVE
    assert pass_result.kind is FacadeResultKind.TURN_PASSED
    assert pass_result.turn_changed
    assert pass_result.snapshot.current_player is not None
    assert pass_result.snapshot.current_player.color is PlayerColor.YELLOW


def test_capture_outcome_is_exposed_through_facade_result() -> None:
    red_piece = outer_piece("red-1", PlayerColor.RED, 0)
    yellow_piece = outer_piece("yellow-1", PlayerColor.YELLOW, 29)
    match = create_match(
        [3],
        (
            player_with_first_piece("red", PlayerColor.RED, red_piece),
            player_with_first_piece("yellow", PlayerColor.YELLOW, yellow_piece),
        ),
    )
    match.turn_engine.set_occupancy(OuterPathOccupancy(global_index=3, pieces=(yellow_piece,)))
    facade = GameFacade.from_match(match)

    facade.roll()
    result = facade.choose_piece("red-1")

    assert result.capture_occurred
    assert result.captured_piece is not None
    assert result.captured_piece.id == "yellow-1"
    assert result.captured_piece.state is PieceState.IN_YARD
    assert result.bonus_available
    assert result.bonus_reasons == frozenset({"capture"})


def test_snapshot_exposes_outer_occupancy_safe_and_protected_status() -> None:
    red_piece_1 = outer_piece("red-1", PlayerColor.RED, 2)
    red_piece_2 = outer_piece("red-2", PlayerColor.RED, 2)
    yellow_piece = outer_piece("yellow-1", PlayerColor.YELLOW, 26)
    match = create_match(
        [3],
        (
            replace(
                Player(id="red", name="Red", color=PlayerColor.RED),
                pieces=(
                    red_piece_1,
                    red_piece_2,
                    outer_piece("red-3", PlayerColor.RED, 4),
                    outer_piece("red-4", PlayerColor.RED, 5),
                ),
            ),
            player_with_first_piece("yellow", PlayerColor.YELLOW, yellow_piece),
        ),
    )
    match.turn_engine.set_occupancy(
        OuterPathOccupancy(global_index=2, pieces=(red_piece_1, red_piece_2))
    )
    match.turn_engine.set_occupancy(
        OuterPathOccupancy(global_index=0, pieces=(yellow_piece,))
    )
    facade = GameFacade.from_match(match)

    occupancies = {
        occupancy.global_index: occupancy for occupancy in facade.snapshot().outer_occupancies
    }

    assert [piece.id for piece in occupancies[2].pieces] == ["red-1", "red-2"]
    assert not occupancies[2].is_safe
    assert occupancies[2].is_protected
    assert occupancies[0].is_safe
    assert occupancies[0].is_protected


def test_finish_outcome_ranking_and_match_completion_are_exposed() -> None:
    red_player = Player(id="red", name="Red", color=PlayerColor.RED)
    finishing_piece = home_piece("red-final", PlayerColor.RED, 4)
    red_player = replace(
        red_player,
        pieces=(
            finished_piece("red-1", PlayerColor.RED),
            finished_piece("red-2", PlayerColor.RED),
            finished_piece("red-3", PlayerColor.RED),
            finishing_piece,
        ),
    )
    match = create_match(
        [1],
        (red_player, Player(id="yellow", name="Yellow", color=PlayerColor.YELLOW)),
    )
    facade = GameFacade.from_match(match)

    facade.roll()
    result = facade.choose_piece("red-final")

    assert result.piece_finished
    assert result.bonus_reasons == frozenset({"finish"})
    assert not result.bonus_available
    assert result.match_completed
    assert result.snapshot.is_complete
    assert result.snapshot.current_player is None
    assert [(entry.rank, entry.color) for entry in result.ranked_players] == [
        (1, PlayerColor.RED),
        (2, PlayerColor.YELLOW),
    ]
    assert [(entry.rank, entry.color) for entry in facade.rankings()] == [
        (1, PlayerColor.RED),
        (2, PlayerColor.YELLOW),
    ]


def test_timer_expiration_result_is_exposed() -> None:
    clock = FixedClock()
    facade = GameFacade()
    facade.start_match(
        ("Alice", "Bob"),
        color_randomizer=FixedColorRandomizer(
            choices=[(PlayerColor.RED, PlayerColor.YELLOW)],
            samples=[(PlayerColor.RED, PlayerColor.YELLOW)],
        ),
        dice=FixedDice([6]),
        clock=clock,
    )

    clock.advance(10)
    result = facade.expire_decision_if_needed()

    assert result.kind is FacadeResultKind.ROLL_TIMEOUT
    assert result.turn_changed
    assert result.snapshot.current_player is not None
    assert result.snapshot.current_player.color is PlayerColor.YELLOW


def test_invalid_roll_phase_is_rejected_cleanly() -> None:
    facade = create_facade([6, 6])
    facade.roll()

    with pytest.raises(GameFacadeError, match="Expected phase"):
        facade.roll()


def test_illegal_piece_selection_is_rejected_cleanly() -> None:
    facade = create_facade([6])
    facade.roll()

    with pytest.raises(GameFacadeError, match="not legal"):
        facade.choose_piece("missing-piece")


def test_move_before_roll_is_rejected_cleanly() -> None:
    facade = create_facade([6])

    with pytest.raises(GameFacadeError, match="Expected phase"):
        facade.choose_piece("player-1-piece-1")


def test_actions_after_match_completion_are_rejected() -> None:
    red_player = Player(id="red", name="Red", color=PlayerColor.RED)
    red_player = replace(
        red_player,
        pieces=tuple(finished_piece(f"red-{index}", PlayerColor.RED) for index in range(4)),
    )
    match = create_match(
        [6],
        (red_player, Player(id="yellow", name="Yellow", color=PlayerColor.YELLOW)),
    )
    match.evaluate_rankings()
    facade = GameFacade.from_match(match)

    with pytest.raises(GameFacadeError, match="complete"):
        facade.roll()


def test_public_snapshot_cannot_mutate_authoritative_domain_state() -> None:
    facade = create_facade([6])
    snapshot = facade.snapshot()

    with pytest.raises(FrozenInstanceError):
        snapshot.players[0].name = "Changed"

    assert facade.current_player().name == "Alice"


def test_player_and_piece_state_queries_return_snapshots() -> None:
    facade = create_facade([6])

    player = facade.current_player()
    piece = facade.piece_state(player.pieces[0].id)

    assert facade.player_state(player.id) == player
    assert piece.owner_color is PlayerColor.RED


def test_queries_before_match_start_are_rejected() -> None:
    facade = GameFacade()

    with pytest.raises(GameFacadeError, match="No match"):
        facade.snapshot()
