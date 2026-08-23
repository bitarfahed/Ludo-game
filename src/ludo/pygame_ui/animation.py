"""Presentation animation state for resolved gameplay events."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from ludo.app import LegalMoveSnapshot, MoveRouteStepSnapshot, PieceSnapshot
from ludo.config import DEFAULT_ANIMATION_SETTINGS, AnimationSettings
from ludo.domain import BoardTopology, PieceState, PlayerColor
from ludo.domain.movement import MoveDestinationKind


class AnimationEvent(StrEnum):
    """Completed animation event identifiers."""

    DICE = "dice"
    MOVE = "move"
    CAPTURE = "capture"
    FINISH = "finish"


@dataclass(frozen=True, slots=True)
class AnimatedPiece:
    """One piece currently drawn by the animation overlay."""

    piece_id: str
    symbol: str
    color_value: str
    source: MoveRouteStepSnapshot | None
    route: tuple[MoveRouteStepSnapshot, ...]
    elapsed_ms: int = 0


@dataclass(frozen=True, slots=True)
class CaptureAnimation:
    """Captured-piece visual return sequence."""

    piece_id: str
    symbol: str
    owner_color: PlayerColor
    color_value: str
    start: MoveRouteStepSnapshot
    elapsed_ms: int = 0


@dataclass(frozen=True, slots=True)
class DiceAnimation:
    """Dice roll animation state that preserves the authoritative final value."""

    final_value: int
    elapsed_ms: int = 0

    def display_value(self) -> int:
        """Return a transient visible value without changing the final result."""
        return self.elapsed_ms // 70 % 6 + 1


@dataclass(slots=True)
class AnimationManager:
    """Advance non-blocking gameplay animations and expose interaction locks."""

    settings: AnimationSettings = DEFAULT_ANIMATION_SETTINGS
    dice: DiceAnimation | None = None
    move: AnimatedPiece | None = None
    capture: CaptureAnimation | None = None
    finish_piece_id: str | None = None
    finish_color: PlayerColor | None = None
    finish_elapsed_ms: int = 0
    _completed: list[AnimationEvent] = field(default_factory=list)

    @property
    def input_locked(self) -> bool:
        """Return whether gameplay clicks should be suspended."""
        return self.dice is not None or self.move is not None or self.capture is not None

    @property
    def hidden_piece_ids(self) -> frozenset[str]:
        """Return piece identifiers currently represented by animation overlays."""
        hidden = set()
        if self.move is not None:
            hidden.add(self.move.piece_id)
        if self.capture is not None:
            hidden.add(self.capture.piece_id)
        return frozenset(hidden)

    def start_dice(self, final_value: int) -> None:
        """Start a dice roll animation for an already resolved dice value."""
        self.dice = DiceAnimation(final_value)

    def start_move(
        self,
        move: LegalMoveSnapshot,
        *,
        moved_piece: PieceSnapshot,
        captured_piece: PieceSnapshot | None = None,
        piece_finished: bool = False,
    ) -> None:
        """Start visual feedback for an already resolved piece move."""
        self.move = AnimatedPiece(
            piece_id=move.piece_id,
            symbol=moved_piece.owner_color.piece_symbol,
            color_value=moved_piece.owner_color.value,
            source=_source_step(move),
            route=move.route,
        )
        if captured_piece is not None and move.route:
            self.capture = CaptureAnimation(
                piece_id=captured_piece.id,
                symbol=captured_piece.owner_color.piece_symbol,
                owner_color=captured_piece.owner_color,
                color_value=captured_piece.owner_color.value,
                start=move.route[-1],
            )
        if piece_finished:
            self.finish_piece_id = move.piece_id
            self.finish_color = moved_piece.owner_color
            self.finish_elapsed_ms = 0

    def update(self, delta_ms: int, *, paused: bool = False) -> None:
        """Advance active animations unless paused."""
        if paused:
            return
        if self.dice is not None:
            self._advance_dice(delta_ms)
        if self.move is not None:
            self._advance_move(delta_ms)
        elif self.capture is not None:
            self._advance_capture(delta_ms)
        if self.finish_piece_id is not None:
            self._advance_finish(delta_ms)

    def pop_completed(self) -> tuple[AnimationEvent, ...]:
        """Return newly completed animation events once."""
        completed = tuple(self._completed)
        self._completed.clear()
        return completed

    def _advance_dice(self, delta_ms: int) -> None:
        if self.dice is None:
            return
        elapsed = self.dice.elapsed_ms + delta_ms
        if elapsed >= self.settings.dice_roll_ms:
            self._completed.append(AnimationEvent.DICE)
            self.dice = None
            return
        self.dice = DiceAnimation(self.dice.final_value, elapsed)

    def _advance_move(self, delta_ms: int) -> None:
        if self.move is None:
            return
        elapsed = self.move.elapsed_ms + delta_ms
        duration = max(1, len(self.move.route)) * self.settings.movement_step_ms
        if elapsed >= duration:
            self._completed.append(AnimationEvent.MOVE)
            self.move = None
            return
        self.move = AnimatedPiece(
            self.move.piece_id,
            self.move.symbol,
            self.move.color_value,
            self.move.source,
            self.move.route,
            elapsed,
        )

    def _advance_capture(self, delta_ms: int) -> None:
        if self.capture is None:
            return
        elapsed = self.capture.elapsed_ms + delta_ms
        duration = self.settings.capture_feedback_ms + self.settings.capture_return_ms
        if elapsed >= duration:
            self._completed.append(AnimationEvent.CAPTURE)
            self.capture = None
            return
        self.capture = CaptureAnimation(
            self.capture.piece_id,
            self.capture.symbol,
            self.capture.owner_color,
            self.capture.color_value,
            self.capture.start,
            elapsed,
        )

    def _advance_finish(self, delta_ms: int) -> None:
        self.finish_elapsed_ms += delta_ms
        if self.finish_elapsed_ms >= self.settings.finish_pulse_ms:
            self._completed.append(AnimationEvent.FINISH)
            self.finish_piece_id = None
            self.finish_color = None
            self.finish_elapsed_ms = 0


def _source_step(move: LegalMoveSnapshot) -> MoveRouteStepSnapshot | None:
    if move.state is PieceState.ON_OUTER_PATH and move.path_progress is not None:
        return MoveRouteStepSnapshot(
            kind=MoveDestinationKind.OUTER_PATH,
            global_outer_index=BoardTopology().global_outer_index(
                move.owner_color, move.path_progress
            ),
        )
    if move.state is PieceState.ON_HOME_PATH and move.path_progress is not None:
        return MoveRouteStepSnapshot(
            kind=MoveDestinationKind.HOME_PATH,
            home_color=move.owner_color,
            home_index=move.path_progress,
        )
    return None
