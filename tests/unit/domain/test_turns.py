"""Unit tests for deterministic turn flow, dice, bonuses, and timers."""

from ludo.domain import (
    FixedClock,
    FixedDice,
    OuterPathOccupancy,
    Piece,
    PieceState,
    Player,
    PlayerColor,
    TurnEngine,
    TurnEventKind,
    TurnPhase,
)


def player(player_id: str, color: PlayerColor, pieces: tuple[Piece, ...] | None = None) -> Player:
    return Player(id=player_id, name=player_id[:10], color=color, pieces=pieces or ())


def player_with_piece(player_id: str, color: PlayerColor, first_piece: Piece) -> Player:
    filler = player(f"{player_id}-fill", color).pieces[:3]
    return player(player_id, color, (first_piece, *filler))


def piece(piece_id: str, color: PlayerColor, progress: int) -> Piece:
    return Piece(
        id=piece_id,
        owner_color=color,
        state=PieceState.ON_OUTER_PATH,
        path_progress=progress,
    )


def engine_with_rolls(rolls: list[int], players: tuple[Player, ...] | None = None) -> TurnEngine:
    return TurnEngine(
        players=players or (player("red", PlayerColor.RED), player("blue", PlayerColor.BLUE)),
        dice=FixedDice(rolls),
        clock=FixedClock(),
    )


def test_normal_roll_move_advances_to_next_player() -> None:
    red_piece = piece("red-1", PlayerColor.RED, 0)
    engine = engine_with_rolls(
        [3],
        players=(
            player_with_piece("red", PlayerColor.RED, red_piece),
            player("blue", PlayerColor.BLUE),
        ),
    )

    roll_event = engine.roll()
    move_event = engine.select_piece("red-1")

    assert roll_event.kind is TurnEventKind.ROLL_ACCEPTED
    assert move_event.kind is TurnEventKind.MOVE_RESOLVED
    assert engine.current_player.color is PlayerColor.BLUE
    assert engine.phase is TurnPhase.WAITING_FOR_ROLL


def test_roll_six_grants_bonus_roll() -> None:
    engine = engine_with_rolls(
        [6], players=(player("red", PlayerColor.RED), player("blue", PlayerColor.BLUE))
    )

    engine.roll()
    event = engine.select_piece("red-piece-1")

    assert event.bonus_granted
    assert event.bonus_reasons == frozenset({"rolled_6"})
    assert engine.current_player.color is PlayerColor.RED
    assert engine.phase is TurnPhase.WAITING_FOR_ROLL


def test_capture_grants_bonus_roll() -> None:
    red_piece = piece("red-1", PlayerColor.RED, 0)
    blue_piece = piece("blue-1", PlayerColor.BLUE, 3)
    engine = engine_with_rolls(
        [3],
        players=(
            player_with_piece("red", PlayerColor.RED, red_piece),
            player_with_piece("blue", PlayerColor.BLUE, blue_piece),
        ),
    )
    engine.set_occupancy(OuterPathOccupancy(global_index=3, pieces=(blue_piece,)))

    engine.roll()
    event = engine.select_piece("red-1")

    assert event.collision_outcome is not None
    assert event.collision_outcome.capture_occurred
    assert event.bonus_reasons == frozenset({"capture"})
    assert engine.current_player.color is PlayerColor.RED


def test_finish_grants_bonus_roll() -> None:
    red_piece = Piece(
        id="red-1",
        owner_color=PlayerColor.RED,
        state=PieceState.ON_HOME_PATH,
        path_progress=4,
    )
    engine = engine_with_rolls(
        [1],
        players=(
            player_with_piece("red", PlayerColor.RED, red_piece),
            player("blue", PlayerColor.BLUE),
        ),
    )

    engine.roll()
    event = engine.select_piece("red-1")

    assert event.bonus_reasons == frozenset({"finish"})
    assert engine.current_player.color is PlayerColor.RED


def test_multiple_bonus_reasons_grant_only_one_bonus_roll() -> None:
    red_piece = piece("red-1", PlayerColor.RED, 0)
    blue_piece = piece("blue-1", PlayerColor.BLUE, 6)
    engine = engine_with_rolls(
        [6],
        players=(
            player_with_piece("red", PlayerColor.RED, red_piece),
            player_with_piece("blue", PlayerColor.BLUE, blue_piece),
        ),
    )
    engine.set_occupancy(OuterPathOccupancy(global_index=6, pieces=(blue_piece,)))

    engine.roll()
    event = engine.select_piece("red-1")

    assert event.bonus_granted
    assert event.bonus_reasons == frozenset({"rolled_6", "capture"})
    assert engine.current_player.color is PlayerColor.RED


def test_bonus_roll_can_generate_another_bonus() -> None:
    engine = engine_with_rolls(
        [6, 6], players=(player("red", PlayerColor.RED), player("blue", PlayerColor.BLUE))
    )

    engine.roll()
    first = engine.select_piece("red-piece-1")
    engine.roll()
    second = engine.select_piece("red-piece-2")

    assert first.bonus_granted
    assert second.bonus_granted
    assert engine.current_player.color is PlayerColor.RED


def test_unusable_roll_grants_no_bonus_even_when_six() -> None:
    finished = tuple(
        Piece(id=f"red-finished-{idx}", owner_color=PlayerColor.RED, state=PieceState.FINISHED)
        for idx in range(4)
    )
    engine = engine_with_rolls(
        [6], players=(player("red", PlayerColor.RED, finished), player("blue", PlayerColor.BLUE))
    )

    event = engine.roll()

    assert event.kind is TurnEventKind.NO_LEGAL_MOVE
    assert not event.bonus_granted
    assert engine.phase is TurnPhase.NO_LEGAL_MOVE
    engine.complete_no_legal_move_notice()
    assert engine.current_player.color is PlayerColor.BLUE


def test_triple_six_cancels_only_third_roll_and_keeps_first_two_moves() -> None:
    engine = engine_with_rolls(
        [6, 6, 6],
        players=(player("red", PlayerColor.RED), player("blue", PlayerColor.BLUE)),
    )

    engine.roll()
    engine.select_piece("red-piece-1")
    engine.roll()
    engine.select_piece("red-piece-2")
    event = engine.roll()

    assert event.kind is TurnEventKind.TRIPLE_SIX_CANCELLED
    assert engine.player_by_color(PlayerColor.RED).pieces[0].state is PieceState.ON_OUTER_PATH
    assert engine.player_by_color(PlayerColor.RED).pieces[1].state is PieceState.ON_OUTER_PATH
    assert engine.current_player.color is PlayerColor.BLUE


def test_non_six_resets_consecutive_six_sequence() -> None:
    red_piece = piece("red-1", PlayerColor.RED, 0)
    blue_piece = piece("blue-1", PlayerColor.BLUE, 10)
    engine = engine_with_rolls(
        [6, 6, 4, 6],
        players=(
            player_with_piece("red", PlayerColor.RED, red_piece),
            player_with_piece("blue", PlayerColor.BLUE, blue_piece),
        ),
    )
    engine.roll()
    engine.select_piece("red-1")
    engine.roll()
    engine.select_piece("red-fill-piece-1")
    engine.set_occupancy(OuterPathOccupancy(global_index=10, pieces=(blue_piece,)))

    engine.roll()
    engine.select_piece("red-1")
    event = engine.roll()

    assert event.kind is TurnEventKind.ROLL_ACCEPTED
    assert engine.phase is TurnPhase.WAITING_FOR_MOVE


def test_roll_timeout_ends_turn() -> None:
    clock = FixedClock()
    engine = TurnEngine(
        players=(player("red", PlayerColor.RED), player("blue", PlayerColor.BLUE)),
        dice=FixedDice([6]),
        clock=clock,
    )

    clock.advance(10)
    event = engine.expire_decision_if_needed()

    assert event is not None
    assert event.kind is TurnEventKind.ROLL_TIMEOUT
    assert engine.current_player.color is PlayerColor.BLUE


def test_move_timeout_ends_turn_without_auto_selecting_piece() -> None:
    clock = FixedClock()
    engine = TurnEngine(
        players=(player("red", PlayerColor.RED), player("blue", PlayerColor.BLUE)),
        dice=FixedDice([6]),
        clock=clock,
    )

    engine.roll()
    clock.advance(10)
    event = engine.expire_decision_if_needed()

    assert event is not None
    assert event.kind is TurnEventKind.MOVE_TIMEOUT
    assert engine.current_player.color is PlayerColor.BLUE
    assert engine.player_by_color(PlayerColor.RED).pieces[0].state is PieceState.IN_YARD


def test_timer_resets_between_roll_and_move_phases() -> None:
    clock = FixedClock()
    engine = TurnEngine(
        players=(player("red", PlayerColor.RED), player("blue", PlayerColor.BLUE)),
        dice=FixedDice([6]),
        clock=clock,
    )

    clock.advance(4)
    engine.roll()

    assert engine.seconds_remaining == 10


def test_active_player_rotation_skips_non_participating_colors() -> None:
    engine = engine_with_rolls(
        [3], players=(player("red", PlayerColor.RED), player("yellow", PlayerColor.YELLOW))
    )

    engine.roll()
    engine.complete_no_legal_move_notice()

    assert engine.current_player.color is PlayerColor.YELLOW


def test_dice_values_are_injected_deterministically() -> None:
    engine = engine_with_rolls([4, 5])

    assert engine.roll().dice_value == 4
    engine.complete_no_legal_move_notice()
    assert engine.roll().dice_value == 5


def test_clock_controls_timeout_deterministically() -> None:
    clock = FixedClock()
    engine = TurnEngine(
        players=(player("red", PlayerColor.RED), player("blue", PlayerColor.BLUE)),
        dice=FixedDice([6]),
        clock=clock,
    )

    clock.advance(9)
    assert engine.expire_decision_if_needed() is None
    clock.advance(1)
    assert engine.expire_decision_if_needed() is not None
