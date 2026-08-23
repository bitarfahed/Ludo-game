"""Live gameplay piece, dice, and HUD rendering."""

from __future__ import annotations

import pygame

from ludo.app import GameSnapshot
from ludo.domain.movement import MoveDestinationKind
from ludo.geometry import BoardGeometry, ScreenRect
from ludo.pygame_ui import theme
from ludo.pygame_ui.animation import AnimationManager, CaptureAnimation
from ludo.pygame_ui.interaction import DestinationPreview
from ludo.pygame_ui.render_models import (
    DiceHudState,
    GameplayRenderState,
    OccupancyInspection,
    PieceRenderGroup,
    PlayerHudState,
)
from ludo.pygame_ui.render_state import (
    build_gameplay_render_state,
)


class GameplayRenderer:
    """Draw live facade snapshot data on top of the static board."""

    def __init__(self, geometry: BoardGeometry | None = None) -> None:
        self.geometry = geometry or BoardGeometry()

    def draw(
        self,
        surface: pygame.Surface,
        snapshot: GameSnapshot,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        preview: DestinationPreview | None = None,
        inspection: OccupancyInspection | None = None,
        animation: AnimationManager | None = None,
    ) -> None:
        """Draw pieces, dice, player status, and timer HUD."""
        state = build_gameplay_render_state(snapshot, self.geometry)
        for player in state.players:
            self._draw_player_hud(surface, player, font, small_font)
        self._draw_dice(surface, state.dice, font, small_font, animation)
        if preview is not None:
            self._draw_destination_preview(surface, preview, small_font)
        self._draw_pieces(surface, state, font, small_font, animation)
        self._draw_legal_piece_rings(surface, state, snapshot)
        if animation is not None:
            self._draw_animation_overlay(surface, animation, font)
        if inspection is not None:
            self._draw_occupancy_inspection(surface, inspection, small_font)

    def _draw_pieces(
        self,
        surface: pygame.Surface,
        state: GameplayRenderState,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        animation: AnimationManager | None,
    ) -> None:
        hidden_ids = animation.hidden_piece_ids if animation is not None else frozenset()
        for group in state.pieces:
            if any(piece.piece_id in hidden_ids for piece in group.pieces):
                continue
            if group.is_stack_placeholder:
                self._draw_stack_summary(surface, group, small_font)
            else:
                piece = group.pieces[0]
                color = theme.color_for_name(piece.color_value)
                radius = min(group.bounds.width, group.bounds.height) // 2
                radius = max(10, min(radius, self.geometry.cell_size // 2 - 3))
                pygame.draw.circle(surface, color, group.center, radius)
                pygame.draw.circle(surface, theme.SURFACE, group.center, radius, width=2)
                label = font.render(piece.symbol, True, theme.SURFACE)
                surface.blit(label, label.get_rect(center=group.center))

    def _draw_stack_summary(
        self, surface: pygame.Surface, group: PieceRenderGroup, font: pygame.font.Font
    ) -> None:
        component_surfaces = [
            (
                component,
                font.render(component.text, True, theme.color_for_name(component.color_value)),
            )
            for component in group.summary_components
        ]
        if not component_surfaces:
            return
        row_width = max(surface.get_width() for _, surface in component_surfaces)
        total_width = sum(surface.get_width() for _, surface in component_surfaces)
        single_row_width = total_width + max(0, len(component_surfaces) - 1) * 5
        max_width = max(group.bounds.width - 6, 28)
        use_column = single_row_width > max_width
        rect_width = min(max_width, row_width + 12 if use_column else single_row_width + 12)
        rect_height = (len(component_surfaces) * 16 + 8) if use_column else 24
        rect = pygame.Rect(0, 0, rect_width, rect_height)
        rect.center = group.center
        pygame.draw.rect(surface, theme.SURFACE, rect, border_radius=5)
        pygame.draw.rect(surface, theme.TEXT, rect, width=2, border_radius=5)
        if use_column:
            y = rect.y + 5
            for _, label in component_surfaces:
                surface.blit(label, label.get_rect(center=(rect.centerx, y + 7)))
                y += 16
            return
        x = rect.x + 6
        for _, label in component_surfaces:
            label_rect = label.get_rect(midleft=(x, rect.centery))
            surface.blit(label, label_rect)
            x = label_rect.right + 5

    def _draw_dice(
        self,
        surface: pygame.Surface,
        dice: DiceHudState,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        animation: AnimationManager | None,
    ) -> None:
        rect = _to_pygame_rect(dice.bounds)
        border = dice.accent_color if dice.roll_available else theme.BORDER
        pygame.draw.rect(surface, theme.SURFACE, rect, border_radius=7)
        pygame.draw.rect(surface, border, rect, width=3, border_radius=7)
        rolling = animation is not None and animation.dice is not None
        if rolling:
            label_text = str(animation.dice.display_value())
        else:
            label_text = str(dice.current_value) if dice.current_value is not None else "Roll"
        label_font = font if dice.current_value is not None or rolling else small_font
        label = label_font.render(label_text, True, theme.TEXT)
        surface.blit(label, label.get_rect(center=(rect.centerx, rect.centery - 3)))
        if rolling:
            hint = small_font.render("...", True, dice.accent_color)
            surface.blit(hint, hint.get_rect(center=(rect.centerx, rect.bottom - 8)))
        elif dice.roll_available:
            hint = small_font.render("ready", True, dice.accent_color)
            surface.blit(hint, hint.get_rect(center=(rect.centerx, rect.bottom - 8)))

    def _draw_player_hud(
        self,
        surface: pygame.Surface,
        player: PlayerHudState,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> None:
        accent = theme.color_for_name(player.color_value)
        label_color = theme.TEXT if player.active else theme.TEXT_MUTED
        label_prefix = "> " if player.active else ""
        label = font.render(f"{label_prefix}{player.name}", True, label_color)
        surface.blit(label, (player.label_area.x + 10, player.label_area.y + 2))
        status = small_font.render(player.status_text, True, label_color)
        surface.blit(status, (player.label_area.x + 10, player.label_area.y + 28))
        if player.active:
            self._draw_timer(surface, player, accent, small_font)

    def _draw_timer(
        self,
        surface: pygame.Surface,
        player: PlayerHudState,
        accent: tuple[int, int, int],
        font: pygame.font.Font,
    ) -> None:
        rect = _to_pygame_rect(player.timer_area)
        pygame.draw.rect(surface, theme.SURFACE, rect, border_radius=4)
        fill_width = max(2, int(rect.width * player.timer_progress))
        fill = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
        pygame.draw.rect(surface, accent, fill, border_radius=4)
        pygame.draw.rect(surface, theme.BORDER, rect, width=1, border_radius=4)
        seconds = player.seconds_remaining if player.seconds_remaining is not None else 0
        label = font.render(f"{seconds}s", True, theme.TEXT)
        surface.blit(label, label.get_rect(center=rect.center))

    def _draw_legal_piece_rings(
        self,
        surface: pygame.Surface,
        state: GameplayRenderState,
        snapshot: GameSnapshot,
    ) -> None:
        legal_ids = {move.piece_id for move in snapshot.legal_moves}
        if not legal_ids:
            return
        for group in state.pieces:
            if not any(piece.piece_id in legal_ids for piece in group.pieces):
                continue
            radius = min(group.bounds.width, group.bounds.height) // 2 + 4
            radius = max(14, min(radius, self.geometry.cell_size // 2 + 4))
            pygame.draw.circle(surface, theme.ACCENT_DARK, group.center, radius, width=3)

    @staticmethod
    def _draw_destination_preview(
        surface: pygame.Surface,
        preview: DestinationPreview,
        font: pygame.font.Font,
    ) -> None:
        rect = _to_pygame_rect(preview.bounds)
        pygame.draw.rect(surface, theme.ACCENT_DARK, rect, width=3, border_radius=4)
        label = font.render(preview.hint, True, theme.TEXT)
        label_rect = label.get_rect(midbottom=(rect.centerx, rect.y - 4))
        background = label_rect.inflate(8, 4)
        pygame.draw.rect(surface, theme.SURFACE, background, border_radius=4)
        pygame.draw.rect(surface, theme.BORDER, background, width=1, border_radius=4)
        surface.blit(label, label_rect)

    @staticmethod
    def _draw_occupancy_inspection(
        surface: pygame.Surface, inspection: OccupancyInspection, font: pygame.font.Font
    ) -> None:
        rect = _to_pygame_rect(inspection.popup)
        pygame.draw.rect(surface, theme.SURFACE, rect, border_radius=6)
        pygame.draw.rect(surface, theme.TEXT, rect, width=2, border_radius=6)
        y = rect.y + 8
        if inspection.is_safe:
            y = _draw_inspection_status(surface, font, "SAFE SQUARE", y, rect)
        if inspection.is_protected:
            y = _draw_inspection_status(surface, font, "PROTECTED BLOCK", y, rect)
        for line in inspection.lines:
            color = theme.color_for_name(line.color_value)
            swatch = pygame.Rect(rect.x + 10, y + 4, 8, 8)
            pygame.draw.rect(surface, color, swatch, border_radius=2)
            label = font.render(f"{line.color_name} x {line.count}", True, theme.TEXT)
            surface.blit(label, (rect.x + 24, y - 1))
            y += 22

    def _draw_animation_overlay(
        self, surface: pygame.Surface, animation: AnimationManager, font: pygame.font.Font
    ) -> None:
        if animation.move is not None and animation.move.route:
            center = self._animated_route_center(
                animation.move.route,
                animation.move.source,
                animation.move.elapsed_ms,
                animation.settings.movement_step_ms,
            )
            self._draw_animated_piece(
                surface, center, animation.move.color_value, animation.move.symbol, font
            )
        if animation.capture is not None:
            center = self._capture_center(animation.capture, animation)
            self._draw_animated_piece(
                surface, center, animation.capture.color_value, animation.capture.symbol, font
            )
        if animation.finish_color is not None:
            self._draw_finish_pulse(surface, animation)

    def _capture_center(
        self, capture: CaptureAnimation, animation: AnimationManager
    ) -> tuple[int, int]:
        start = self._route_step_center(capture.start)
        if capture.elapsed_ms <= animation.settings.capture_feedback_ms:
            return start
        yard = self.geometry.yard_piece_positions(capture.owner_color)[0]
        elapsed = capture.elapsed_ms - animation.settings.capture_feedback_ms
        fraction = min(1.0, elapsed / max(1, animation.settings.capture_return_ms))
        return _lerp_point(start, yard, fraction)

    def _animated_route_center(
        self,
        route: tuple,
        source,
        elapsed_ms: int,
        step_duration_ms: int,
    ) -> tuple[int, int]:
        step_duration = max(1, step_duration_ms)
        index = min(len(route) - 1, elapsed_ms // step_duration)
        if source is None and index == 0:
            return self._route_step_center(route[0])
        start = self._route_step_center(source if index == 0 else route[index - 1])
        end = self._route_step_center(route[index])
        fraction = min(1.0, (elapsed_ms % step_duration) / step_duration)
        return _lerp_point(start, end, fraction)

    def _route_step_center(self, step) -> tuple[int, int]:
        if step.kind is MoveDestinationKind.OUTER_PATH and step.global_outer_index is not None:
            return self.geometry.outer_square(step.global_outer_index).center
        if (
            step.kind is MoveDestinationKind.HOME_PATH
            and step.home_color is not None
            and step.home_index is not None
        ):
            return self.geometry.home_path_square(step.home_color, step.home_index).center
        if step.kind is MoveDestinationKind.FINISHED and step.home_color is not None:
            return self.geometry.finish_region(step.home_color).center
        return self.geometry.center_dice_area.center

    def _draw_animated_piece(
        self,
        surface: pygame.Surface,
        center: tuple[int, int],
        color_value: str,
        symbol: str,
        font: pygame.font.Font,
    ) -> None:
        radius = max(12, self.geometry.cell_size // 2 - 1)
        pygame.draw.circle(surface, theme.color_for_name(color_value), center, radius)
        pygame.draw.circle(surface, theme.SURFACE, center, radius, width=3)
        label = font.render(symbol, True, theme.SURFACE)
        surface.blit(label, label.get_rect(center=center))

    def _draw_finish_pulse(self, surface: pygame.Surface, animation: AnimationManager) -> None:
        if animation.finish_color is None:
            return
        rect = _to_pygame_rect(self.geometry.finish_region(animation.finish_color))
        fraction = animation.finish_elapsed_ms / max(1, animation.settings.finish_pulse_ms)
        radius = int(max(rect.width, rect.height) * (0.45 + 0.2 * min(1.0, fraction)))
        pygame.draw.circle(
            surface,
            theme.color_for_name(animation.finish_color.value),
            rect.center,
            radius,
            width=3,
        )


def _draw_inspection_status(
    surface: pygame.Surface, font: pygame.font.Font, text: str, y: int, rect: pygame.Rect
) -> int:
    label = font.render(text, True, theme.TEXT)
    background = pygame.Rect(rect.x + 8, y - 2, rect.width - 16, 18)
    pygame.draw.rect(surface, theme.BACKGROUND, background, border_radius=4)
    surface.blit(label, label.get_rect(center=background.center))
    return y + 22


def _lerp_point(
    start: tuple[int, int], end: tuple[int, int], fraction: float
) -> tuple[int, int]:
    return (
        int(start[0] + (end[0] - start[0]) * fraction),
        int(start[1] + (end[1] - start[1]) * fraction),
    )


def _to_pygame_rect(rect: ScreenRect) -> pygame.Rect:
    return pygame.Rect(rect.x, rect.y, rect.width, rect.height)
