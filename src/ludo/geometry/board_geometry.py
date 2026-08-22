"""Logical-to-screen board geometry for static Ludo rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from ludo.domain.board import HOME_PATH_LENGTH, OUTER_PATH_LENGTH, BoardTopology
from ludo.domain.colors import PlayerColor
from ludo.geometry.grid import (
    DEFAULT_BOARD_SIZE,
    DEFAULT_WINDOW_SIZE,
    FINISH_GRIDS,
    GRID_SIZE,
    HOME_GRID_PATHS,
    OUTER_GRID_PATH,
    YARD_GRIDS,
)


class BoardHitKind(StrEnum):
    """Board geometry hit-test result kind."""

    OUTER = "outer"
    HOME_PATH = "home_path"
    YARD = "yard"
    FINISH = "finish"
    DICE = "dice"


@dataclass(frozen=True, slots=True)
class ScreenRect:
    """Small immutable rectangle independent from Pygame."""

    x: int
    y: int
    width: int
    height: int

    @property
    def center(self) -> tuple[int, int]:
        """Return the rectangle center point."""
        return (self.x + self.width // 2, self.y + self.height // 2)

    def contains(self, point: tuple[int, int]) -> bool:
        """Return whether a point lies inside this rectangle."""
        px, py = point
        return self.x <= px < self.x + self.width and self.y <= py < self.y + self.height


@dataclass(frozen=True, slots=True)
class BoardHit:
    """Logical board area found under a screen point."""

    kind: BoardHitKind
    outer_index: int | None = None
    color: PlayerColor | None = None
    home_index: int | None = None


@dataclass(frozen=True, slots=True)
class BoardGeometry:
    """Map logical Ludo board positions to screen rectangles."""

    window_size: tuple[int, int] = DEFAULT_WINDOW_SIZE
    board_size: int = DEFAULT_BOARD_SIZE
    topology: BoardTopology = field(default_factory=BoardTopology)

    def __post_init__(self) -> None:
        if len(OUTER_GRID_PATH) != OUTER_PATH_LENGTH:
            msg = "Outer grid path must contain exactly 52 positions."
            raise ValueError(msg)

    @property
    def cell_size(self) -> int:
        """Return square-grid cell size."""
        return self.board_size // GRID_SIZE

    @property
    def board_rect(self) -> ScreenRect:
        """Return the full board rectangle."""
        width, height = self.window_size
        return ScreenRect(
            (width - self.board_size) // 2,
            (height - self.board_size) // 2,
            self.board_size,
            self.board_size,
        )

    @property
    def outer_squares(self) -> dict[int, ScreenRect]:
        """Return all shared outer-path squares by global index."""
        return {
            index: self._grid_rect(column, row)
            for index, (column, row) in enumerate(OUTER_GRID_PATH)
        }

    @property
    def safe_squares(self) -> dict[int, ScreenRect]:
        """Return all safe outer-path squares by global index."""
        return {
            index: self.outer_square(index) for index in sorted(self.topology.safe_outer_positions)
        }

    def outer_square(self, global_index: int) -> ScreenRect:
        """Return one outer-path square rectangle."""
        self.topology.is_safe_outer_position(global_index)
        column, row = OUTER_GRID_PATH[global_index]
        return self._grid_rect(column, row)

    def home_path_square(self, color: PlayerColor, index: int) -> ScreenRect:
        """Return one private Home-Path square rectangle."""
        self.topology.home_path(color)[index]
        column, row = HOME_GRID_PATHS[color][index]
        return self._grid_rect(column, row)

    def home_path_squares(self, color: PlayerColor) -> tuple[ScreenRect, ...]:
        """Return all private Home-Path square rectangles for a color."""
        return tuple(self.home_path_square(color, index) for index in range(HOME_PATH_LENGTH))

    def yard_region(self, color: PlayerColor) -> ScreenRect:
        """Return a color's Yard region."""
        column, row, width, height = YARD_GRIDS[color]
        return self._grid_rect(column, row, width, height)

    def yard_piece_positions(self, color: PlayerColor) -> tuple[tuple[int, int], ...]:
        """Return four placeholder Yard piece centers for a color."""
        yard = self.yard_region(color)
        quarter = yard.width // 4
        return (
            (yard.x + quarter, yard.y + quarter),
            (yard.x + yard.width - quarter, yard.y + quarter),
            (yard.x + quarter, yard.y + yard.height - quarter),
            (yard.x + yard.width - quarter, yard.y + yard.height - quarter),
        )

    def finish_region(self, color: PlayerColor) -> ScreenRect:
        """Return a color's Finished region."""
        column, row = FINISH_GRIDS[color]
        return self._grid_rect(column, row)

    @property
    def center_dice_area(self) -> ScreenRect:
        """Return the central dice placeholder area."""
        return self._grid_rect(7, 7)

    def player_label_area(self, color: PlayerColor) -> ScreenRect:
        """Return a player-name label area near the color's Yard."""
        yard = self.yard_region(color)
        return ScreenRect(yard.x, yard.y + 8, yard.width, 30)

    def timer_area(self, color: PlayerColor) -> ScreenRect:
        """Return a future timer area near the color's Yard."""
        yard = self.yard_region(color)
        return ScreenRect(yard.x + 18, yard.y + yard.height - 42, yard.width - 36, 24)

    def hit_test(self, point: tuple[int, int]) -> BoardHit | None:
        """Return the logical board area under a screen point when practical."""
        for index, rect in self.outer_squares.items():
            if rect.contains(point):
                return BoardHit(BoardHitKind.OUTER, outer_index=index)
        for color in PlayerColor:
            for index, rect in enumerate(self.home_path_squares(color)):
                if rect.contains(point):
                    return BoardHit(BoardHitKind.HOME_PATH, color=color, home_index=index)
            if self.finish_region(color).contains(point):
                return BoardHit(BoardHitKind.FINISH, color=color)
            if self.yard_region(color).contains(point):
                return BoardHit(BoardHitKind.YARD, color=color)
        if self.center_dice_area.contains(point):
            return BoardHit(BoardHitKind.DICE)
        return None

    def _grid_rect(self, column: int, row: int, width: int = 1, height: int = 1) -> ScreenRect:
        origin = self.board_rect
        cell = self.cell_size
        return ScreenRect(
            origin.x + column * cell,
            origin.y + row * cell,
            width * cell,
            height * cell,
        )
