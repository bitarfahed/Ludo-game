"""Small reusable controls for the Pygame shell."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from ludo.pygame_ui import theme


@dataclass(slots=True)
class Button:
    """Rectangular text button with a command identifier."""

    command: str
    label: str
    rect: pygame.Rect
    enabled: bool = True

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the button."""
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.enabled and self.rect.collidepoint(mouse_pos)
        color = theme.ACCENT_DARK if hovered else theme.ACCENT
        if not self.enabled:
            color = theme.SURFACE_MUTED
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        text_color = theme.SURFACE if self.enabled else theme.TEXT_MUTED
        label = font.render(self.label, True, text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def command_at(self, position: tuple[int, int]) -> str | None:
        """Return this button's command when clicked."""
        if self.enabled and self.rect.collidepoint(position):
            return self.command
        return None


@dataclass(slots=True)
class TextField:
    """Simple single-line text input model with a rectangle."""

    index: int
    rect: pygame.Rect

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        value: str,
        active: bool,
    ) -> None:
        """Draw the text field."""
        pygame.draw.rect(surface, theme.SURFACE, self.rect, border_radius=6)
        border = theme.ACCENT if active else theme.BORDER
        pygame.draw.rect(surface, border, self.rect, width=2, border_radius=6)
        text = font.render(value or f"Player {self.index + 1}", True, _text_color(value))
        surface.blit(text, (self.rect.x + 14, self.rect.y + 12))

    def contains(self, position: tuple[int, int]) -> bool:
        """Return whether a point is inside the text field."""
        return self.rect.collidepoint(position)


def draw_text(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    position: tuple[int, int],
    color: tuple[int, int, int] = theme.TEXT,
) -> None:
    """Draw text at a top-left position."""
    surface.blit(font.render(text, True, color), position)


def _text_color(value: str) -> tuple[int, int, int]:
    return theme.TEXT if value else theme.TEXT_MUTED
