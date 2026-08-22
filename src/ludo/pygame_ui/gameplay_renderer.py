"""Live gameplay piece, dice, and HUD rendering."""

from __future__ import annotations

import pygame

from ludo.app import GameSnapshot
from ludo.geometry import BoardGeometry, ScreenRect
from ludo.pygame_ui import theme
from ludo.pygame_ui.render_models import (
    DiceHudState,
    GameplayRenderState,
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
    ) -> None:
        """Draw pieces, dice, player status, and timer HUD."""
        state = build_gameplay_render_state(snapshot, self.geometry)
        for player in state.players:
            self._draw_player_hud(surface, player, font, small_font)
        self._draw_dice(surface, state.dice, font, small_font)
        self._draw_pieces(surface, state, font, small_font)

    def _draw_pieces(
        self,
        surface: pygame.Surface,
        state: GameplayRenderState,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> None:
        for group in state.pieces:
            if group.is_stack_placeholder:
                self._draw_stack_placeholder(surface, group, small_font)
            else:
                piece = group.pieces[0]
                color = theme.color_for_name(piece.color_value)
                radius = min(group.bounds.width, group.bounds.height) // 2
                radius = max(10, min(radius, self.geometry.cell_size // 2 - 3))
                pygame.draw.circle(surface, color, group.center, radius)
                pygame.draw.circle(surface, theme.SURFACE, group.center, radius, width=2)
                label = font.render(piece.symbol, True, theme.SURFACE)
                surface.blit(label, label.get_rect(center=group.center))

    def _draw_stack_placeholder(
        self, surface: pygame.Surface, group: PieceRenderGroup, font: pygame.font.Font
    ) -> None:
        rect = pygame.Rect(group.center[0] - 18, group.center[1] - 11, 36, 22)
        pygame.draw.rect(surface, theme.TEXT, rect, border_radius=5)
        pygame.draw.rect(surface, theme.SURFACE, rect, width=1, border_radius=5)
        label = font.render(group.placeholder_label or "", True, theme.SURFACE)
        surface.blit(label, label.get_rect(center=rect.center))

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


def _to_pygame_rect(rect: ScreenRect) -> pygame.Rect:
    return pygame.Rect(rect.x, rect.y, rect.width, rect.height)
