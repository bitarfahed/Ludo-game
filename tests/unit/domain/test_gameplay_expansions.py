"""Tests for bonus die, hazards, and backward capture extensions."""

from dataclasses import replace

import pytest

from ludo.domain import (
    BoardTopology,
    FixedClock,
    FixedDice,
    FixedHazardRandomizer,
    FixedSpecialDie,
    Match,
    MoveActionKind,
    MovementRules,
    OuterPathOccupancy,
    Piece,
    PieceState,
    Player,
    PlayerColor,
    TurnEngine,
    TurnEventKind,
    TurnPhase,
    generate_hazards,
    generate_special_squares,
)
from ludo.domain.bonus_die import SPECIAL_BONUS_VALUE, RandomSpecialDie
from ludo.domain.hazards import clamped_backward_relative_progress
from ludo.domain.match import FixedColorRandomizer

ALL_COLORS = (
    PlayerColor.RED,
    PlayerColor.GREEN,
    PlayerColor.YELLOW,
    PlayerColor.BLUE,
)


def player(player_id: str, color: PlayerColor, pieces: tuple[Piece, ...] | None = None) -> Player:
    """Create a player with optional custom pieces."""
    base = Player(id=player_id, name=player_id[:10], color=color)
    return replace(base, pieces=pieces) if pieces is not None else base


def outer_piece(piece_id: str, color: PlayerColor, progress: int) -> Piece:
    """Create one outer-path piece."""
    return Piece(piece_id, color, PieceState.ON_OUTER_PATH, progress)


def home_piece(piece_id: str, color: PlayerColor, progress: int) -> Piece:
    """Create one Home-Path piece."""
    return Piece(piece_id, color, PieceState.ON_HOME_PATH, progress)


def player_with_piece(player_id: str, color: PlayerColor, piece: Piece) -> Player:
    """Create a player with one focused piece and three completed placeholders."""
    return player(
        player_id,
        color,
        (
            piece,
            Piece(f"{player_id}-finished-1", color, PieceState.FINISHED),
            Piece(f"{player_id}-finished-2", color, PieceState.FINISHED),
            Piece(f"{player_id}-finished-3", color, PieceState.FINISHED),
        ),
    )


def engine(
    *,
    rolls: list[int],
    specials: list[int] | None = None,
    red_piece: Piece | None = None,
    blue_piece: Piece | None = None,
    hazards: frozenset[int] = frozenset(),
) -> TurnEngine:
    """Build a focused two-player turn engine."""
    red = player(
        "red",
        PlayerColor.RED,
        (
            red_piece or outer_piece("red-1", PlayerColor.RED, 0),
            Piece("red-finished-1", PlayerColor.RED, PieceState.FINISHED),
            Piece("red-finished-2", PlayerColor.RED, PieceState.FINISHED),
            Piece("red-finished-3", PlayerColor.RED, PieceState.FINISHED),
        ),
    )
    blue = player(
        "blue",
        PlayerColor.BLUE,
        (
            blue_piece or Piece("blue-yard", PlayerColor.BLUE, PieceState.IN_YARD),
            Piece("blue-finished-1", PlayerColor.BLUE, PieceState.FINISHED),
            Piece("blue-finished-2", PlayerColor.BLUE, PieceState.FINISHED),
            Piece("blue-finished-3", PlayerColor.BLUE, PieceState.FINISHED),
        ),
    )
    return TurnEngine(
        players=(red, blue),
        dice=FixedDice(rolls),
        special_die=FixedSpecialDie(specials or [0] * 20),
        clock=FixedClock(),
        hazard_positions=hazards,
    )


def engine_for_color(
    *,
    color: PlayerColor,
    piece: Piece,
    rolls: list[int],
    hazards: frozenset[int] = frozenset(),
    opponent_piece: Piece | None = None,
) -> TurnEngine:
    """Build a focused engine with the requested color taking the current turn."""
    opponent_color = next(candidate for candidate in PlayerColor if candidate is not color)
    opponent = (
        player_with_piece("opponent", opponent_color, opponent_piece)
        if opponent_piece is not None
        else player("opponent", opponent_color)
    )
    return TurnEngine(
        players=(player_with_piece("moving", color, piece), opponent),
        dice=FixedDice(rolls),
        special_die=FixedSpecialDie([0] * 20),
        clock=FixedClock(),
        hazard_positions=hazards,
    )


def roll_special_to_move(turn_engine: TurnEngine):
    base = turn_engine.roll()
    special = turn_engine.roll_special()
    return base, special


def test_random_special_die_probability_boundary_is_configurable() -> None:
    class BoundaryRandom:
        def __init__(self, value: float) -> None:
            self.value = value

        def random(self) -> float:
            return self.value

    assert RandomSpecialDie(BoundaryRandom(0.19), success_probability=0.20).roll_bonus() == 2
    assert RandomSpecialDie(BoundaryRandom(0.20), success_probability=0.20).roll_bonus() == 0


def test_special_bonus_creates_effective_movement_without_six_bonus() -> None:
    turn_engine = engine(rolls=[4], specials=[2])

    base, special = roll_special_to_move(turn_engine)

    assert base.dice_value == 4
    assert special.special_bonus == SPECIAL_BONUS_VALUE
    assert {action.movement_value for action in turn_engine.legal_actions} == {4, 6}
    move = turn_engine.select_piece("red-1", "red-1:forward:6")
    assert move.moved_piece.path_progress == 6
    assert not move.bonus_granted
    assert turn_engine.current_player.color is PlayerColor.BLUE


def test_synthetic_six_cannot_release_yard_piece() -> None:
    red = Piece("red-1", PlayerColor.RED, PieceState.IN_YARD)
    turn_engine = engine(rolls=[4], specials=[2], red_piece=red)

    turn_engine.roll()
    event = turn_engine.roll_special()

    assert event.kind is TurnEventKind.NO_LEGAL_MOVE
    assert turn_engine.phase is TurnPhase.NO_LEGAL_MOVE


def test_real_base_six_can_release_yard_piece_with_special_success() -> None:
    red = Piece("red-1", PlayerColor.RED, PieceState.IN_YARD)
    turn_engine = engine(rolls=[6], specials=[2], red_piece=red)

    turn_engine.roll()
    turn_engine.roll_special()

    assert {action.action_id for action in turn_engine.legal_actions} == {"red-1:forward:6"}


def test_real_base_six_with_special_moves_eight_and_keeps_six_bonus() -> None:
    turn_engine = engine(rolls=[6], specials=[2])

    roll_special_to_move(turn_engine)
    move = turn_engine.select_piece("red-1", "red-1:forward:8")

    assert move.approved_movement_value == 8
    assert move.moved_piece.path_progress == 8
    assert move.bonus_reasons == frozenset({"rolled_6"})
    assert turn_engine.current_player.color is PlayerColor.RED


def test_third_consecutive_base_six_cancels_before_special_roll() -> None:
    turn_engine = engine(rolls=[6, 6, 6], specials=[0, 0, 2])

    roll_special_to_move(turn_engine)
    turn_engine.select_piece("red-1")
    roll_special_to_move(turn_engine)
    turn_engine.select_piece("red-1")
    event = turn_engine.roll()

    assert event.kind is TurnEventKind.TRIPLE_SIX_CANCELLED
    assert turn_engine.special_die.bonuses == [2]


def test_special_bonus_falls_back_when_effective_illegal_but_base_legal() -> None:
    turn_engine = engine(rolls=[2], specials=[2], red_piece=home_piece("red-1", PlayerColor.RED, 3))

    turn_engine.roll()
    roll = turn_engine.roll_special()
    move = turn_engine.select_piece("red-1")

    assert roll.special_bonus == 2
    assert not roll.special_bonus_applied
    assert roll.approved_movement_value is None
    assert move.moved_piece.state is PieceState.FINISHED


def test_special_roll_with_no_effective_or_base_move_enters_no_legal_phase() -> None:
    turn_engine = engine(rolls=[2], specials=[2], red_piece=home_piece("red-1", PlayerColor.RED, 4))

    turn_engine.roll()
    event = turn_engine.roll_special()

    assert event.kind is TurnEventKind.NO_LEGAL_MOVE
    assert turn_engine.phase is TurnPhase.NO_LEGAL_MOVE


def test_effective_backward_capture_prevents_base_fallback() -> None:
    red = outer_piece("red-1", PlayerColor.RED, 10)
    blue = outer_piece("blue-1", PlayerColor.BLUE, (4 - 39) % 52)
    turn_engine = engine(rolls=[4], specials=[2], red_piece=red, blue_piece=blue)
    turn_engine.set_occupancy(OuterPathOccupancy(4, (blue,)))

    turn_engine.roll()
    event = turn_engine.roll_special()

    assert event.approved_movement_value is None
    assert any(
        action.kind is MoveActionKind.BACKWARD_CAPTURE for action in turn_engine.legal_actions
    )


SPECIAL_SEQUENCE = [1, 2, 3, 4, 14, 15, 16, 17, 27, 28, 29, 30, 40, 41, 42, 43]


def test_special_square_generation_has_required_distribution_and_no_safe_overlap() -> None:
    layout = generate_special_squares(FixedHazardRandomizer(SPECIAL_SEQUENCE.copy()))
    hazards = generate_hazards(FixedHazardRandomizer(SPECIAL_SEQUENCE.copy()))

    assert layout.hazards == frozenset({1, 2, 14, 15, 27, 28, 40, 41})
    assert layout.boosts == frozenset({3, 16, 29, 42})
    assert layout.shields == frozenset({4, 17, 30, 43})
    assert hazards == layout.hazards
    assert {sector: sum(index // 13 == sector for index in hazards) for sector in range(4)} == {
        0: 2,
        1: 2,
        2: 2,
        3: 2,
    }
    assert len(layout.all_positions) == 16
    assert hazards.isdisjoint(BoardTopology().safe_outer_positions)
    assert layout.all_positions.isdisjoint(BoardTopology().safe_outer_positions)


def test_match_exposes_fixed_hazard_positions() -> None:
    match = Match.create(
        ("Alice", "Bob"),
        color_randomizer=FixedColorRandomizer(
            choices=[(PlayerColor.RED, PlayerColor.YELLOW)],
            samples=[(PlayerColor.RED, PlayerColor.YELLOW)],
        ),
        hazard_randomizer=FixedHazardRandomizer(SPECIAL_SEQUENCE.copy()),
        dice=FixedDice([1]),
        special_die=FixedSpecialDie([0]),
        clock=FixedClock(),
    )

    assert match.turn_engine.hazard_positions == frozenset({1, 2, 14, 15, 27, 28, 40, 41})
    assert match.turn_engine.boost_positions == frozenset({3, 16, 29, 42})
    assert match.turn_engine.shield_square_positions == frozenset({4, 17, 30, 43})


def test_passing_over_hazard_does_not_trigger_penalty() -> None:
    turn_engine = engine(rolls=[3], hazards=frozenset({2}))

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert not event.hazard_triggered
    assert event.moved_piece.path_progress == 3


def test_direct_hazard_landing_moves_piece_two_outer_steps_backward() -> None:
    turn_engine = engine(rolls=[3], hazards=frozenset({3}))

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert event.hazard_triggered
    assert event.hazard_from == 3
    assert event.hazard_to == 1
    assert event.moved_piece.path_progress == 1


def test_hazard_penalty_at_start_stays_at_start() -> None:
    assert clamped_backward_relative_progress(0) == 0


@pytest.mark.parametrize("color", ALL_COLORS)
def test_hazard_penalty_near_start_clamps_to_start_for_every_color(
    color: PlayerColor,
) -> None:
    topology = BoardTopology()
    hazard_index = topology.global_outer_index(color, 1)
    piece = outer_piece(f"{color.value}-1", color, 0)
    turn_engine = engine_for_color(
        color=color,
        piece=piece,
        rolls=[1],
        hazards=frozenset({hazard_index}),
    )

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece(piece.id)

    assert event.hazard_triggered
    assert event.hazard_from == hazard_index
    assert event.hazard_to == topology.start_position(color)
    assert event.moved_piece.path_progress == 0


def test_hazard_penalty_near_start_does_not_wrap_to_outer_index_51() -> None:
    turn_engine = engine(rolls=[1], hazards=frozenset({1}))

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert event.hazard_to == 0
    assert event.hazard_to != 51
    assert event.moved_piece.path_progress == 0


@pytest.mark.parametrize("color", ALL_COLORS)
def test_early_hazard_clamp_cannot_create_premature_home_entry(
    color: PlayerColor,
) -> None:
    topology = BoardTopology()
    hazard_index = topology.global_outer_index(color, 1)
    piece = outer_piece(f"{color.value}-1", color, 0)
    turn_engine = engine_for_color(
        color=color,
        piece=piece,
        rolls=[1],
        hazards=frozenset({hazard_index}),
    )

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece(piece.id)
    next_move = MovementRules().propose_move(event.moved_piece, 6)

    assert next_move is not None
    assert next_move.piece.state is PieceState.ON_OUTER_PATH
    assert next_move.piece.path_progress == 6


@pytest.mark.parametrize("color", ALL_COLORS)
def test_home_entry_still_works_after_genuine_full_outer_lap(color: PlayerColor) -> None:
    piece = outer_piece(f"{color.value}-1", color, 51)
    turn_engine = engine_for_color(color=color, piece=piece, rolls=[1])

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece(piece.id)

    assert event.moved_piece.state is PieceState.ON_HOME_PATH
    assert event.moved_piece.path_progress == 0


@pytest.mark.parametrize("color", ALL_COLORS)
def test_clamped_hazard_start_square_remains_safe_and_protected(
    color: PlayerColor,
) -> None:
    topology = BoardTopology()
    hazard_index = topology.global_outer_index(color, 1)
    start_index = topology.start_position(color)
    opponent_color = next(candidate for candidate in PlayerColor if candidate is not color)
    opponent_progress = (start_index - topology.start_position(opponent_color)) % 52
    opponent_piece = outer_piece("opponent-1", opponent_color, opponent_progress)
    piece = outer_piece(f"{color.value}-1", color, 0)
    turn_engine = engine_for_color(
        color=color,
        piece=piece,
        rolls=[1],
        hazards=frozenset({hazard_index}),
        opponent_piece=opponent_piece,
    )
    turn_engine.set_occupancy(OuterPathOccupancy(start_index, (opponent_piece,)))

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece(piece.id)

    assert event.hazard_to == start_index
    assert not event.collision_outcome.capture_occurred
    assert event.collision_outcome.destination_protected


def test_hazard_penalty_destination_can_capture() -> None:
    blue = outer_piece("blue-1", PlayerColor.BLUE, (1 - 39) % 52)
    turn_engine = engine(rolls=[3], blue_piece=blue, hazards=frozenset({3}))
    turn_engine.set_occupancy(OuterPathOccupancy(1, (blue,)))

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert event.hazard_triggered
    assert event.collision_outcome.capture_occurred
    assert event.bonus_reasons == frozenset({"capture"})


def test_hazard_penalty_can_land_on_safe_square_without_capture() -> None:
    blue = outer_piece("blue-1", PlayerColor.BLUE, (0 - 39) % 52)
    turn_engine = engine(rolls=[2], blue_piece=blue, hazards=frozenset({2}))
    turn_engine.set_occupancy(OuterPathOccupancy(0, (blue,)))

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert event.hazard_to == 0
    assert not event.collision_outcome.capture_occurred
    assert event.collision_outcome.destination_protected


def test_hazard_penalty_can_join_protected_block_without_capture() -> None:
    blue_1 = outer_piece("blue-1", PlayerColor.BLUE, (1 - 39) % 52)
    blue_2 = outer_piece("blue-2", PlayerColor.BLUE, (1 - 39) % 52)
    turn_engine = engine(rolls=[3], hazards=frozenset({3}))
    turn_engine.set_occupancy(OuterPathOccupancy(1, (blue_1, blue_2)))

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert event.hazard_to == 1
    assert not event.collision_outcome.capture_occurred
    assert event.collision_outcome.destination_protected


def test_hazard_penalty_does_not_chain_to_second_hazard() -> None:
    turn_engine = engine(rolls=[3], hazards=frozenset({1, 3}))

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert event.hazard_from == 3
    assert event.hazard_to == 1
    assert event.moved_piece.path_progress == 1


def test_boost_direct_landing_moves_piece_two_outer_steps_forward() -> None:
    turn_engine = engine(rolls=[3])
    turn_engine.boost_positions = frozenset({3})

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert event.boost_triggered
    assert event.boost_from == 3
    assert event.boost_to == 5
    assert event.moved_piece.path_progress == 5


def test_boost_forward_displacement_still_uses_existing_wrap_behavior() -> None:
    red = outer_piece("red-1", PlayerColor.RED, 50)
    turn_engine = engine(rolls=[1], red_piece=red)
    turn_engine.boost_positions = frozenset({51})

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert event.boost_triggered
    assert event.boost_from == 51
    assert event.boost_to == 1
    assert event.moved_piece.path_progress == 1


def test_passing_over_boost_or_shield_does_not_trigger_effect() -> None:
    turn_engine = engine(rolls=[3])
    turn_engine.boost_positions = frozenset({2})
    turn_engine.shield_square_positions = frozenset({1})

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert not event.boost_triggered
    assert not event.shield_acquired
    assert event.moved_piece.path_progress == 3
    assert not event.moved_piece.has_shield


def test_boost_forced_destination_can_capture_and_grant_bonus() -> None:
    blue = outer_piece("blue-1", PlayerColor.BLUE, (5 - 39) % 52)
    turn_engine = engine(rolls=[3], blue_piece=blue)
    turn_engine.boost_positions = frozenset({3})
    turn_engine.set_occupancy(OuterPathOccupancy(5, (blue,)))

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert event.boost_triggered
    assert event.collision_outcome.capture_occurred
    assert event.bonus_reasons == frozenset({"capture"})


def test_boost_forced_destination_does_not_chain_other_special_squares() -> None:
    turn_engine = engine(rolls=[3])
    turn_engine.boost_positions = frozenset({3, 5})
    turn_engine.hazard_positions = frozenset({5})
    turn_engine.shield_square_positions = frozenset({5})

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert event.boost_triggered
    assert not event.hazard_triggered
    assert not event.shield_acquired
    assert event.moved_piece.path_progress == 5
    assert not event.moved_piece.has_shield


def test_shield_square_direct_landing_grants_one_shield() -> None:
    turn_engine = engine(rolls=[3])
    turn_engine.shield_square_positions = frozenset({3})

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert event.shield_acquired
    assert event.moved_piece.has_shield


def test_shield_does_not_stack_when_already_carried() -> None:
    red = outer_piece("red-1", PlayerColor.RED, 0)
    red = replace(red, has_shield=True)
    turn_engine = engine(rolls=[3], red_piece=red)
    turn_engine.shield_square_positions = frozenset({3})

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert not event.shield_acquired
    assert event.moved_piece.has_shield


def test_forward_capture_consumes_shield_without_capture_bonus() -> None:
    blue = replace(outer_piece("blue-1", PlayerColor.BLUE, (3 - 39) % 52), has_shield=True)
    turn_engine = engine(rolls=[3], blue_piece=blue)
    turn_engine.set_occupancy(OuterPathOccupancy(3, (blue,)))

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert event.shield_broken
    assert not event.collision_outcome.capture_occurred
    assert event.collision_outcome.captured_piece is None
    assert event.bonus_reasons == frozenset()
    assert turn_engine.player_by_color(PlayerColor.BLUE).pieces[0].state is PieceState.ON_OUTER_PATH
    assert not turn_engine.player_by_color(PlayerColor.BLUE).pieces[0].has_shield


def test_shield_can_be_reacquired_after_consumption() -> None:
    blue = replace(outer_piece("blue-1", PlayerColor.BLUE, (3 - 39) % 52), has_shield=True)
    turn_engine = engine(rolls=[3], blue_piece=blue)
    turn_engine.set_occupancy(OuterPathOccupancy(3, (blue,)))

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert event.shield_broken
    unshielded = turn_engine.player_by_color(PlayerColor.BLUE).pieces[0]
    assert not unshielded.has_shield
    reacquire_engine = TurnEngine(
        players=(
            player(
                "blue",
                PlayerColor.BLUE,
                (
                    unshielded,
                    Piece("blue-finished-1", PlayerColor.BLUE, PieceState.FINISHED),
                    Piece("blue-finished-2", PlayerColor.BLUE, PieceState.FINISHED),
                    Piece("blue-finished-3", PlayerColor.BLUE, PieceState.FINISHED),
                ),
            ),
            player("red", PlayerColor.RED),
        ),
        dice=FixedDice([3]),
        special_die=FixedSpecialDie([0]),
        clock=FixedClock(),
        shield_square_positions=frozenset({6}),
    )
    roll_special_to_move(reacquire_engine)
    reacquired = reacquire_engine.select_piece("blue-1")
    assert reacquired.moved_piece.has_shield


def test_hazard_ignores_shield_and_keeps_it_after_displacement() -> None:
    red = replace(outer_piece("red-1", PlayerColor.RED, 0), has_shield=True)
    turn_engine = engine(rolls=[3], red_piece=red, hazards=frozenset({3}))

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1")

    assert event.hazard_triggered
    assert event.moved_piece.path_progress == 1
    assert event.moved_piece.has_shield


def test_backward_capture_is_legal_only_for_vulnerable_opponent_at_exact_distance() -> None:
    red = outer_piece("red-1", PlayerColor.RED, 10)
    blue = outer_piece("blue-1", PlayerColor.BLUE, (7 - 39) % 52)
    turn_engine = engine(rolls=[3], red_piece=red, blue_piece=blue)
    turn_engine.set_occupancy(OuterPathOccupancy(7, (blue,)))

    roll_special_to_move(turn_engine)

    assert "red-1:backward_capture:3" in {
        action.action_id for action in turn_engine.legal_actions
    }


def test_shielded_target_does_not_expose_backward_capture() -> None:
    red = outer_piece("red-1", PlayerColor.RED, 10)
    blue = replace(outer_piece("blue-1", PlayerColor.BLUE, (7 - 39) % 52), has_shield=True)
    turn_engine = engine(rolls=[3], red_piece=red, blue_piece=blue)
    turn_engine.set_occupancy(OuterPathOccupancy(7, (blue,)))

    roll_special_to_move(turn_engine)

    assert all(
        action.kind is not MoveActionKind.BACKWARD_CAPTURE
        for action in turn_engine.legal_actions
    )


def test_backward_capture_is_not_general_backward_movement() -> None:
    red = outer_piece("red-1", PlayerColor.RED, 10)
    turn_engine = engine(rolls=[3], red_piece=red)

    roll_special_to_move(turn_engine)

    assert "red-1:backward_capture:3" not in {
        action.action_id for action in turn_engine.legal_actions
    }


def test_backward_capture_does_not_wrap_before_start() -> None:
    red = outer_piece("red-1", PlayerColor.RED, 1)
    blue = outer_piece("blue-1", PlayerColor.BLUE, (50 - 39) % 52)
    turn_engine = engine(rolls=[3], red_piece=red, blue_piece=blue)
    turn_engine.set_occupancy(OuterPathOccupancy(50, (blue,)))

    roll_special_to_move(turn_engine)

    assert all(
        action.kind is not MoveActionKind.BACKWARD_CAPTURE
        for action in turn_engine.legal_actions
    )


def test_backward_capture_rejects_safe_and_protected_destinations() -> None:
    red = outer_piece("red-1", PlayerColor.RED, 3)
    blue_safe = outer_piece("blue-safe", PlayerColor.BLUE, (0 - 39) % 52)
    turn_engine = engine(rolls=[3], red_piece=red, blue_piece=blue_safe)
    turn_engine.set_occupancy(OuterPathOccupancy(0, (blue_safe,)))

    roll_special_to_move(turn_engine)

    assert all(
        action.kind is not MoveActionKind.BACKWARD_CAPTURE
        for action in turn_engine.legal_actions
    )


def test_successful_backward_capture_returns_opponent_to_yard_and_grants_bonus() -> None:
    red = outer_piece("red-1", PlayerColor.RED, 10)
    blue = outer_piece("blue-1", PlayerColor.BLUE, (7 - 39) % 52)
    turn_engine = engine(rolls=[3], red_piece=red, blue_piece=blue)
    turn_engine.set_occupancy(OuterPathOccupancy(7, (blue,)))

    roll_special_to_move(turn_engine)
    event = turn_engine.select_piece("red-1", "red-1:backward_capture:3")

    assert event.action_kind is MoveActionKind.BACKWARD_CAPTURE
    assert event.collision_outcome.capture_occurred
    assert event.collision_outcome.captured_piece.state is PieceState.IN_YARD
    assert event.moved_piece.path_progress == 7
    assert event.bonus_reasons == frozenset({"capture"})


def test_shield_is_removed_on_home_path_entry_and_finished() -> None:
    red = replace(outer_piece("red-1", PlayerColor.RED, 51), has_shield=True)
    enter_home = engine(rolls=[1], red_piece=red)

    roll_special_to_move(enter_home)
    home_event = enter_home.select_piece("red-1")

    assert home_event.moved_piece.state is PieceState.ON_HOME_PATH
    assert not home_event.moved_piece.has_shield

    finish_piece = replace(home_piece("red-1", PlayerColor.RED, 4), has_shield=False)
    finish_engine = engine(rolls=[1], red_piece=finish_piece)
    roll_special_to_move(finish_engine)
    finish_event = finish_engine.select_piece("red-1")

    assert finish_event.moved_piece.state is PieceState.FINISHED
    assert not finish_event.moved_piece.has_shield
