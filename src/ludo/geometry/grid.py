"""Static 15x15 Ludo grid coordinate tables."""

from __future__ import annotations

from ludo.domain.colors import PlayerColor

GRID_SIZE = 15
DEFAULT_BOARD_SIZE = 570
DEFAULT_WINDOW_SIZE = (960, 640)

OUTER_GRID_PATH = (
    (0, 6),
    (1, 6),
    (2, 6),
    (3, 6),
    (4, 6),
    (5, 6),
    (6, 5),
    (6, 4),
    (6, 3),
    (6, 2),
    (6, 1),
    (6, 0),
    (7, 0),
    (8, 0),
    (8, 1),
    (8, 2),
    (8, 3),
    (8, 4),
    (8, 5),
    (9, 6),
    (10, 6),
    (11, 6),
    (12, 6),
    (13, 6),
    (14, 6),
    (14, 7),
    (14, 8),
    (13, 8),
    (12, 8),
    (11, 8),
    (10, 8),
    (9, 8),
    (8, 9),
    (8, 10),
    (8, 11),
    (8, 12),
    (8, 13),
    (8, 14),
    (7, 14),
    (6, 14),
    (6, 13),
    (6, 12),
    (6, 11),
    (6, 10),
    (6, 9),
    (5, 8),
    (4, 8),
    (3, 8),
    (2, 8),
    (1, 8),
    (0, 8),
    (0, 7),
)

HOME_GRID_PATHS = {
    PlayerColor.RED: ((1, 7), (2, 7), (3, 7), (4, 7), (5, 7)),
    PlayerColor.GREEN: ((7, 1), (7, 2), (7, 3), (7, 4), (7, 5)),
    PlayerColor.YELLOW: ((13, 7), (12, 7), (11, 7), (10, 7), (9, 7)),
    PlayerColor.BLUE: ((7, 13), (7, 12), (7, 11), (7, 10), (7, 9)),
}

YARD_GRIDS = {
    PlayerColor.RED: (0, 0, 6, 6),
    PlayerColor.GREEN: (9, 0, 6, 6),
    PlayerColor.YELLOW: (9, 9, 6, 6),
    PlayerColor.BLUE: (0, 9, 6, 6),
}

FINISH_GRIDS = {
    PlayerColor.RED: (6, 7),
    PlayerColor.GREEN: (7, 6),
    PlayerColor.YELLOW: (8, 7),
    PlayerColor.BLUE: (7, 8),
}

CENTER_NON_TRAVERSABLE_GRIDS = (
    (6, 6),
    (8, 6),
    (6, 8),
    (8, 8),
)
