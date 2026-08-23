"""Tests for bonus die, hazards, and backward capture extensions."""

from dataclasses import replace

from ludo.domain import (
    BoardTopology,
    FixedClock,
    FixedDice,
    FixedHazardRandomizer,
    FixedSpecialDie,
    Match,
    MoveActionKind,
    OuterPathOccupancy,
    Piece,
    PieceState,
    Player,
    PlayerColor,
    TurnEngine,
    TurnEventKind,
    TurnPhase,
    generate_hazards,
)
from ludo.domain.bonus_die import SPECIAL_BONUS_VALUE, RandomSpecialDie
from ludo.domain.match import FixedColorRandomizer


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
    red = outer_piece("red-1", PlayerColor.RED, 4)
    blue = outer_piece("blue-1", PlayerColor.BLUE, 50 - 39)
    turn_engine = engine(rolls=[4], specials=[2], red_piece=red, blue_piece=blue)
    turn_engine.set_occupancy(OuterPathOccupancy(50, (blue,)))

    turn_engine.roll()
    event = turn_engine.roll_special()

    assert event.approved_movement_value is None
    assert any(
        action.kind is MoveActionKind.BACKWARD_CAPTURE for action in turn_engine.legal_actions
    )


def test_hazard_generation_has_one_per_sector_and_no_safe_overlap() -> None:
    hazards = generate_hazards(FixedHazardRandomizer([1, 14, 27, 40]))

    assert hazards == frozenset({1, 14, 27, 40})
    assert {hazard // 13 for hazard in hazards} == {0, 1, 2, 3}
    assert hazards.isdisjoint(BoardTopology().safe_outer_positions)


def test_match_exposes_fixed_hazard_positions() -> None:
    match = Match.create(
        ("Alice", "Bob"),
        color_randomizer=FixedColorRandomizer(
            choices=[(PlayerColor.RED, PlayerColor.YELLOW)],
            samples=[(PlayerColor.RED, PlayerColor.YELLOW)],
        ),
        hazard_randomizer=FixedHazardRandomizer([1, 14, 27, 40]),
        dice=FixedDice([1]),
        special_die=FixedSpecialDie([0]),
        clock=FixedClock(),
    )

    assert match.turn_engine.hazard_positions == frozenset({1, 14, 27, 40})


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


def test_backward_capture_is_legal_only_for_vulnerable_opponent_at_exact_distance() -> None:
    red = outer_piece("red-1", PlayerColor.RED, 10)
    blue = outer_piece("blue-1", PlayerColor.BLUE, (7 - 39) % 52)
    turn_engine = engine(rolls=[3], red_piece=red, blue_piece=blue)
    turn_engine.set_occupancy(OuterPathOccupancy(7, (blue,)))

    roll_special_to_move(turn_engine)

    assert "red-1:backward_capture:3" in {
        action.action_id for action in turn_engine.legal_actions
    }


def test_backward_capture_is_not_general_backward_movement() -> None:
    red = outer_piece("red-1", PlayerColor.RED, 10)
    turn_engine = engine(rolls=[3], red_piece=red)

    roll_special_to_move(turn_engine)

    assert "red-1:backward_capture:3" not in {
        action.action_id for action in turn_engine.legal_actions
    }


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
