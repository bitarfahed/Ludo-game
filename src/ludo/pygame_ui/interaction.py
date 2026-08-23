"""Mouse interaction controller for gameplay screen actions."""

from __future__ import annotations

from dataclasses import dataclass, field

from ludo.app import FacadeResult, GameFacadeError, LegalMoveSnapshot, MoveDestinationSnapshot
from ludo.audio import AudioService
from ludo.domain.turns import TurnPhase
from ludo.geometry import BoardGeometry, ScreenRect
from ludo.pygame_ui.animation import AnimationManager
from ludo.pygame_ui.render_models import OccupancyInspection
from ludo.pygame_ui.render_state import (
    build_gameplay_render_state,
    build_occupancy_inspection,
)
from ludo.pygame_ui.state import ScreenController, ScreenState


@dataclass(frozen=True, slots=True)
class DestinationPreview:
    """Current legal-move hover preview."""

    piece_id: str
    bounds: ScreenRect
    hint: str


@dataclass(slots=True)
class GameplayInteractionController:
    """Translate mouse positions into facade gameplay commands."""

    geometry: BoardGeometry
    animation: AnimationManager = field(default_factory=AnimationManager)
    audio: AudioService = field(default_factory=AudioService)
    preview: DestinationPreview | None = None
    inspection: OccupancyInspection | None = None
    latest_result: FacadeResult | None = None

    def handle_click(self, position: tuple[int, int], controller: ScreenController) -> bool:
        """Handle one gameplay click and return whether it was consumed."""
        if self.animation.input_locked:
            return False
        if not _can_interact(controller):
            return False
        snapshot = controller.snapshot()
        if snapshot is None:
            return False
        if self.geometry.base_die_area.contains(position):
            return self._try_base_roll(controller)
        if self.geometry.special_die_area.contains(position):
            return self._try_special_roll(controller)
        destination_move = self._legal_destination_at(position, snapshot)
        if destination_move is not None:
            return self._try_choose_piece(
                controller, destination_move.piece_id, destination_move.action_id
            )
        piece_id = self._legal_piece_at(position, snapshot)
        if piece_id is None:
            return False
        return self._try_choose_piece(controller, piece_id, None)

    def handle_hover(self, position: tuple[int, int], controller: ScreenController) -> None:
        """Update legal destination preview for a mouse position."""
        self.preview = None
        self.inspection = None
        if not _can_interact(controller):
            return
        snapshot = controller.snapshot()
        if snapshot is None:
            return
        self.inspection = build_occupancy_inspection(snapshot, self.geometry, position)
        destination_move = self._legal_destination_at(position, snapshot)
        if destination_move is not None:
            bounds = self._destination_bounds(destination_move.destination)
            if bounds is not None:
                self.preview = DestinationPreview(
                    destination_move.piece_id,
                    bounds,
                    _action_hint(destination_move),
                )
            return
        piece_id = self._legal_piece_at(position, snapshot)
        if piece_id is None:
            return
        matches = _legal_moves_by_id(snapshot.legal_moves, piece_id)
        if len(matches) != 1:
            return
        legal_move = matches[0]
        bounds = self._destination_bounds(legal_move.destination)
        if bounds is not None:
            self.preview = DestinationPreview(
                piece_id,
                bounds,
                _action_hint(legal_move),
            )

    def _try_base_roll(self, controller: ScreenController) -> bool:
        if controller.facade is None:
            return False
        snapshot = controller.facade.snapshot()
        if snapshot.phase is not TurnPhase.WAITING_FOR_ROLL or not snapshot.current_player:
            return False
        try:
            result = controller.facade.roll()
        except GameFacadeError:
            return False
        if result.dice_value is not None:
            self.animation.start_dice(result.dice_value)
        self.audio.play_result(result)
        self.preview = None
        self.inspection = None
        self.latest_result = result
        return True

    def _try_special_roll(self, controller: ScreenController) -> bool:
        if controller.facade is None:
            return False
        snapshot = controller.facade.snapshot()
        if snapshot.phase is not TurnPhase.WAITING_FOR_SPECIAL_ROLL or not snapshot.current_player:
            return False
        try:
            result = controller.facade.roll_special()
        except GameFacadeError:
            return False
        self.animation.start_dice(result.special_bonus)
        self.audio.play_result(result)
        self.preview = None
        self.inspection = None
        self.latest_result = result
        return True

    def _try_choose_piece(
        self, controller: ScreenController, piece_id: str, action_id: str | None
    ) -> bool:
        if controller.facade is None:
            return False
        snapshot = controller.facade.snapshot()
        legal_move = _legal_move_by_action(snapshot.legal_moves, piece_id, action_id)
        if legal_move is None:
            return False
        try:
            result = controller.facade.choose_piece(piece_id, action_id)
        except GameFacadeError:
            return False
        if result.moved_piece is not None:
            self.animation.start_move(
                legal_move,
                moved_piece=result.moved_piece,
                captured_piece=result.captured_piece,
                piece_finished=result.piece_finished,
            )
        self.audio.play_result(result)
        self.preview = None
        self.inspection = None
        self.latest_result = result
        return True

    def _legal_piece_at(self, position: tuple[int, int], snapshot) -> str | None:
        legal_piece_ids = {move.piece_id for move in snapshot.legal_moves}
        if not legal_piece_ids:
            return None
        render_state = build_gameplay_render_state(snapshot, self.geometry)
        for group in render_state.pieces:
            if not group.bounds.contains(position):
                continue
            for piece in group.pieces:
                if piece.piece_id in legal_piece_ids:
                    return piece.piece_id
        return None

    def _legal_destination_at(
        self, position: tuple[int, int], snapshot
    ) -> LegalMoveSnapshot | None:
        for move in snapshot.legal_moves:
            bounds = self._destination_bounds(move.destination)
            if bounds is not None and bounds.contains(position):
                return move
        return None

    def pop_result(self) -> FacadeResult | None:
        """Return the latest facade result once."""
        result = self.latest_result
        self.latest_result = None
        return result

    def _destination_bounds(self, destination: MoveDestinationSnapshot) -> ScreenRect | None:
        if destination.kind.value == "outer_path" and destination.global_outer_index is not None:
            return self.geometry.outer_square(destination.global_outer_index)
        if (
            destination.kind.value == "home_path"
            and destination.home_color is not None
            and destination.home_index is not None
        ):
            return self.geometry.home_path_square(destination.home_color, destination.home_index)
        if destination.kind.value == "finished" and destination.home_color is not None:
            return self.geometry.finish_region(destination.home_color)
        return None


def _can_interact(controller: ScreenController) -> bool:
    return (
        controller.screen is ScreenState.GAME
        and not controller.paused
        and not controller.gameplay_input_blocked
        and controller.facade is not None
    )


def _legal_move_by_id(
    legal_moves: tuple[LegalMoveSnapshot, ...], piece_id: str
) -> LegalMoveSnapshot | None:
    for move in legal_moves:
        if move.piece_id == piece_id:
            return move
    return None


def _legal_moves_by_id(
    legal_moves: tuple[LegalMoveSnapshot, ...], piece_id: str
) -> tuple[LegalMoveSnapshot, ...]:
    return tuple(move for move in legal_moves if move.piece_id == piece_id)


def _legal_move_by_action(
    legal_moves: tuple[LegalMoveSnapshot, ...], piece_id: str, action_id: str | None
) -> LegalMoveSnapshot | None:
    matches = _legal_moves_by_id(legal_moves, piece_id)
    if action_id is not None:
        for move in matches:
            if move.action_id == action_id:
                return move
        return None
    return matches[0] if len(matches) == 1 else None


def _action_hint(move: LegalMoveSnapshot) -> str:
    if move.action_kind.value == "backward_capture":
        return f"Backward {move.movement_value}"
    suffix = " (+2)" if move.movement_value != move.dice_value else ""
    return f"Use {move.movement_value}{suffix}"
