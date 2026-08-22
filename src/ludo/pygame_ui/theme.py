"""Shared visual constants for the early Pygame shell."""

from __future__ import annotations

WINDOW_SIZE = (960, 640)
FPS = 60

BACKGROUND = (246, 247, 250)
SURFACE = (255, 255, 255)
SURFACE_MUTED = (232, 236, 242)
TEXT = (31, 36, 48)
TEXT_MUTED = (95, 104, 121)
ACCENT = (33, 115, 225)
ACCENT_DARK = (19, 83, 169)
DANGER = (184, 48, 64)
OVERLAY = (20, 24, 32, 180)
BORDER = (197, 204, 216)

COLOR_SWATCHES = {
    "red": (218, 58, 73),
    "green": (47, 145, 89),
    "yellow": (232, 184, 56),
    "blue": (54, 111, 214),
}


def color_for_name(color_name: str) -> tuple[int, int, int]:
    """Return a display color for a Ludo color value."""
    return COLOR_SWATCHES.get(color_name, TEXT_MUTED)
