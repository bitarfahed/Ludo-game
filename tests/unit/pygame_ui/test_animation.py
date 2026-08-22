"""Tests for non-blocking gameplay animation state."""

from ludo.app import (
    LegalMoveSnapshot,
    MoveDestinationSnapshot,
    MoveRouteStepSnapshot,
    PieceSnapshot,
)
from ludo.config import AnimationSettings
from ludo.domain import PieceState, PlayerColor
from ludo.domain.movement import MoveDestinationKind
from ludo.pygame_ui.animation import AnimationEvent, AnimationManager


def route(*indices: int) -> tuple[MoveRouteStepSnapshot, ...]:
    return tuple(
        MoveRouteStepSnapshot(MoveDestinationKind.OUTER_PATH, global_outer_index=index)
        for index in indices
    )


def legal_move(route_steps: tuple[MoveRouteStepSnapshot, ...]) -> LegalMoveSnapshot:
    return LegalMoveSnapshot(
        piece_id="red-1",
        owner_color=PlayerColor.RED,
        state=PieceState.ON_OUTER_PATH,
        path_progress=0,
        dice_value=3,
        destination=MoveDestinationSnapshot(
            MoveDestinationKind.OUTER_PATH,
            global_outer_index=route_steps[-1].global_outer_index,
        ),
        route=route_steps,
    )


def piece(piece_id: str, color: PlayerColor) -> PieceSnapshot:
    return PieceSnapshot(piece_id, color, PieceState.ON_OUTER_PATH, 0)


def test_movement_animation_receives_correct_route_and_progresses() -> None:
    manager = AnimationManager(AnimationSettings(movement_step_ms=100))
    move = legal_move(route(1, 2, 3))

    manager.start_move(move, moved_piece=piece("red-1", PlayerColor.RED))
    manager.update(150)

    assert manager.move is not None
    assert manager.move.route == move.route
    assert manager.move.elapsed_ms == 150
    assert manager.input_locked


def test_completion_is_reported_once() -> None:
    manager = AnimationManager(AnimationSettings(movement_step_ms=100))
    manager.start_move(legal_move(route(1)), moved_piece=piece("red-1", PlayerColor.RED))

    manager.update(100)

    assert manager.move is None
    assert manager.pop_completed() == (AnimationEvent.MOVE,)
    assert manager.pop_completed() == ()


def test_capture_animation_sequence_order() -> None:
    manager = AnimationManager(
        AnimationSettings(movement_step_ms=100, capture_feedback_ms=50, capture_return_ms=50)
    )
    manager.start_move(
        legal_move(route(1, 2)),
        moved_piece=piece("red-1", PlayerColor.RED),
        captured_piece=piece("blue-1", PlayerColor.BLUE),
    )

    manager.update(200)
    assert manager.pop_completed() == (AnimationEvent.MOVE,)
    assert manager.capture is not None

    manager.update(100)
    assert manager.pop_completed() == (AnimationEvent.CAPTURE,)
    assert manager.capture is None


def test_finish_animation_completion() -> None:
    manager = AnimationManager(AnimationSettings(movement_step_ms=100, finish_pulse_ms=50))
    manager.start_move(
        legal_move(route(1)),
        moved_piece=PieceSnapshot("red-1", PlayerColor.RED, PieceState.FINISHED, None),
        piece_finished=True,
    )

    manager.update(50)

    assert AnimationEvent.FINISH in manager.pop_completed()
    assert manager.finish_piece_id is None


def test_dice_animation_preserves_authoritative_final_result() -> None:
    manager = AnimationManager(AnimationSettings(dice_roll_ms=100))
    manager.start_dice(5)

    assert manager.dice is not None
    assert manager.dice.final_value == 5
    assert 1 <= manager.dice.display_value() <= 6

    manager.update(100)

    assert manager.dice is None
    assert manager.pop_completed() == (AnimationEvent.DICE,)


def test_pause_freezes_and_resume_continues_animation() -> None:
    manager = AnimationManager(AnimationSettings(movement_step_ms=100))
    manager.start_move(legal_move(route(1, 2)), moved_piece=piece("red-1", PlayerColor.RED))

    manager.update(80, paused=True)
    assert manager.move is not None
    assert manager.move.elapsed_ms == 0

    manager.update(80, paused=False)
    assert manager.move is not None
    assert manager.move.elapsed_ms == 80
