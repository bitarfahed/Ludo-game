"""Live gameplay piece, dice, and HUD rendering."""

from __future__ import annotations

import pygame

from ludo.app import GameSnapshot
from ludo.geometry import BoardGeometry, ScreenRect
from ludo.pygame_ui import theme
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
    ) -> None:
        """Draw pieces, dice, player status, and timer HUD."""
        state = build_gameplay_render_state(snapshot, self.geometry)
        for player in state.players:
            self._draw_player_hud(surface, player, font, small_font)
        self._draw_dice(surface, state.dice, font, small_font)
        if preview is not None:
            self._draw_destination_preview(surface, preview, small_font)
        self._draw_pieces(surface, state, font, small_font)
        self._draw_legal_piece_rings(surface, state, snapshot)
        if inspection is not None:
            self._draw_occupancy_inspection(surface, inspection, small_font)

    def _draw_pieces(
        self,
        surface: pygame.Surface,
        state: GameplayRenderState,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> None:
        for group in state.pieces:
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
    ) -> None:
        rect = _to_pygame_rect(dice.bounds)
        border = dice.accent_color if dice.roll_available else theme.BORDER
        pygame.draw.rect(surface, theme.SURFACE, rect, border_radius=7)
        pygame.draw.rect(surface, border, rect, width=3, border_radius=7)
        label_text = str(dice.current_value) if dice.current_value is not None else "Roll"
        label_font = font if dice.current_value is not None else small_font
        label = label_font.render(label_text, True, theme.TEXT)
        surface.blit(label, label.get_rect(center=(rect.centerx, rect.centery - 3)))
        if dice.roll_available:
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


def _draw_inspection_status(
    surface: pygame.Surface, font: pygame.font.Font, text: str, y: int, rect: pygame.Rect
) -> int:
    label = font.render(text, True, theme.TEXT)
    background = pygame.Rect(rect.x + 8, y - 2, rect.width - 16, 18)
    pygame.draw.rect(surface, theme.BACKGROUND, background, border_radius=4)
    surface.blit(label, label.get_rect(center=background.center))
    return y + 22


def _to_pygame_rect(rect: ScreenRect) -> pygame.Rect:
    return pygame.Rect(rect.x, rect.y, rect.width, rect.height)
