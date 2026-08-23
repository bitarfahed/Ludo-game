"""Static Ludo board rendering for the Pygame game screen."""

from __future__ import annotations

import pygame

from ludo.app import GameSnapshot
from ludo.domain.colors import PlayerColor
from ludo.geometry import BoardGeometry, ScreenRect
from ludo.pygame_ui import theme
from ludo.pygame_ui.controls import draw_text


class BoardRenderer:
    """Draw the static board from geometry and public facade snapshots."""

    def __init__(self, geometry: BoardGeometry | None = None) -> None:
        self.geometry = geometry or BoardGeometry()

    def draw(
        self,
        surface: pygame.Surface,
        snapshot: GameSnapshot,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> None:
        """Draw all static board regions."""
        _draw_shadowed_rect(surface, self.geometry.board_rect, theme.SURFACE)
        self._draw_yards(surface, snapshot, font)
        self._draw_outer_path(surface, snapshot, font)
        self._draw_home_paths(surface)
        self._draw_finish_regions(surface, small_font)
        self._draw_center_dice_area(surface, small_font)

    def _draw_yards(
        self,
        surface: pygame.Surface,
        snapshot: GameSnapshot,
        font: pygame.font.Font,
    ) -> None:
        players_by_color = {player.color: player for player in snapshot.players}
        current_color = snapshot.current_player.color if snapshot.current_player else None
        for color in PlayerColor:
            yard = self.geometry.yard_region(color)
            inactive = color in snapshot.inactive_colors
            base = _muted_color(color) if inactive else _soft_color(color)
            _draw_shadowed_rect(surface, yard, base)
            border_width = 2 if inactive or color != current_color else 4
            pygame.draw.rect(surface, _color(color), _to_pygame_rect(yard), border_width)
            self._draw_yard_piece_placeholders(surface, color, inactive)
            if color not in players_by_color:
                label_area = self.geometry.player_label_area(color)
                draw_text(surface, font, "Inactive", _rect_text_pos(label_area), theme.TEXT_MUTED)

    def _draw_yard_piece_placeholders(
        self, surface: pygame.Surface, color: PlayerColor, inactive: bool
    ) -> None:
        fill = theme.SURFACE_MUTED if inactive else theme.SURFACE
        outline = theme.BORDER if inactive else _color(color)
        radius = self.geometry.cell_size // 2
        for center in self.geometry.yard_piece_positions(color):
            pygame.draw.circle(surface, fill, center, radius)
            pygame.draw.circle(surface, outline, center, radius, width=3)

    def _draw_outer_path(
        self, surface: pygame.Surface, snapshot: GameSnapshot, font: pygame.font.Font
    ) -> None:
        for index, rect in self.geometry.outer_squares.items():
            fill = theme.SURFACE
            if index in self.geometry.topology.start_positions.values():
                fill = _soft_color(_start_color_for(index, self.geometry))
            elif index in self.geometry.topology.star_safe_positions:
                fill = (249, 251, 255)
            pygame.draw.rect(surface, fill, _to_pygame_rect(rect))
            pygame.draw.rect(surface, theme.BORDER, _to_pygame_rect(rect), width=1)
            pygame.draw.rect(surface, theme.TEXT_MUTED, _to_pygame_rect(rect), width=2)
            if index in self.geometry.safe_squares:
                marker = "S" if index in self.geometry.topology.start_positions.values() else "*"
                label = font.render(marker, True, theme.TEXT_MUTED)
                surface.blit(label, label.get_rect(center=rect.center))
            if index in snapshot.hazard_positions:
                label = font.render("!", True, theme.DANGER)
                surface.blit(label, label.get_rect(center=(rect.center[0], rect.center[1] + 1)))

    def _draw_home_paths(self, surface: pygame.Surface) -> None:
        for color in PlayerColor:
            for rect in self.geometry.home_path_squares(color):
                pygame.draw.rect(surface, _soft_color(color), _to_pygame_rect(rect))
                pygame.draw.rect(surface, _color(color), _to_pygame_rect(rect), width=2)

    def _draw_finish_regions(self, surface: pygame.Surface, small_font: pygame.font.Font) -> None:
        for color in PlayerColor:
            rect = self.geometry.finish_region(color)
            pygame.draw.rect(surface, _color(color), _to_pygame_rect(rect))
            label = small_font.render("F", True, theme.SURFACE)
            surface.blit(label, label.get_rect(center=rect.center))

    def _draw_center_dice_area(self, surface: pygame.Surface, small_font: pygame.font.Font) -> None:
        rect = self.geometry.center_dice_area
        pygame.draw.rect(surface, theme.SURFACE_MUTED, _to_pygame_rect(rect), border_radius=6)
        pygame.draw.rect(surface, theme.BORDER, _to_pygame_rect(rect), width=2, border_radius=6)
        pygame.draw.line(
            surface,
            theme.BORDER,
            (rect.x, rect.y + rect.height // 2),
            (rect.x + rect.width, rect.y + rect.height // 2),
            width=1,
        )
        normal = small_font.render("N", True, theme.TEXT_MUTED)
        special = small_font.render("S", True, theme.TEXT_MUTED)
        surface.blit(normal, normal.get_rect(center=self.geometry.base_die_area.center))
        surface.blit(special, special.get_rect(center=self.geometry.special_die_area.center))


def _draw_shadowed_rect(
    surface: pygame.Surface, rect: ScreenRect, fill: tuple[int, int, int]
) -> None:
    shadow = pygame.Rect(rect.x + 3, rect.y + 4, rect.width, rect.height)
    pygame.draw.rect(surface, (215, 220, 230), shadow, border_radius=8)
    pygame.draw.rect(surface, fill, _to_pygame_rect(rect), border_radius=8)


def _to_pygame_rect(rect: ScreenRect) -> pygame.Rect:
    return pygame.Rect(rect.x, rect.y, rect.width, rect.height)


def _rect_text_pos(rect: ScreenRect) -> tuple[int, int]:
    return (rect.x + 10, rect.y + 4)


def _color(color: PlayerColor) -> tuple[int, int, int]:
    return theme.color_for_name(color.value)


def _soft_color(color: PlayerColor) -> tuple[int, int, int]:
    red, green, blue = _color(color)
    return ((red + 510) // 3, (green + 510) // 3, (blue + 510) // 3)


def _muted_color(color: PlayerColor) -> tuple[int, int, int]:
    red, green, blue = _soft_color(color)
    return (
        (red + 2 * theme.SURFACE_MUTED[0]) // 3,
        (green + 2 * theme.SURFACE_MUTED[1]) // 3,
        (blue + 2 * theme.SURFACE_MUTED[2]) // 3,
    )


def _start_color_for(index: int, geometry: BoardGeometry) -> PlayerColor:
    for color, start_index in geometry.topology.start_positions.items():
        if start_index == index:
            return color
    msg = f"Outer index {index} is not a start square."
    raise ValueError(msg)
