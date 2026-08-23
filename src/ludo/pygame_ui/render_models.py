"""Draw-ready gameplay render-state models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ludo.geometry import ScreenRect


class PieceLocationKind(StrEnum):
    """Geometry category used to place a rendered piece."""

    YARD = "yard"
    OUTER = "outer"
    HOME = "home"
    FINISH = "finish"


@dataclass(frozen=True, slots=True)
class PieceLocationKey:
    """Logical render location used for grouping pieces."""

    kind: PieceLocationKind
    color_value: str
    index: int | None = None


@dataclass(frozen=True, slots=True)
class PieceRenderItem:
    """One piece prepared for drawing."""

    piece_id: str
    symbol: str
    color_value: str
    location: PieceLocationKey


@dataclass(frozen=True, slots=True)
class StackSummaryComponent:
    """One colored count/symbol part of a stack summary."""

    count: int
    symbol: str
    color_value: str

    @property
    def text(self) -> str:
        """Return approved compact stack notation for this component."""
        return f"{self.count}{self.symbol}"


@dataclass(frozen=True, slots=True)
class OccupancyInspectionLine:
    """One count line in the hover inspection panel."""

    color_name: str
    color_value: str
    count: int


@dataclass(frozen=True, slots=True)
class OccupancyInspection:
    """Detailed hover inspection state for an occupied board square."""

    anchor: ScreenRect
    popup: ScreenRect
    lines: tuple[OccupancyInspectionLine, ...]
    is_safe: bool = False
    is_protected: bool = False


@dataclass(frozen=True, slots=True)
class PieceRenderGroup:
    """Pieces sharing one render location."""

    center: tuple[int, int]
    bounds: ScreenRect
    pieces: tuple[PieceRenderItem, ...]
    summary_components: tuple[StackSummaryComponent, ...] = ()
    inspection: OccupancyInspection | None = None

    @property
    def is_stack_placeholder(self) -> bool:
        """Return whether this group should draw a compact placeholder."""
        return bool(self.summary_components)


@dataclass(frozen=True, slots=True)
class DiceHudState:
    """Center dice display state."""

    bounds: ScreenRect
    base_bounds: ScreenRect
    special_bounds: ScreenRect
    current_value: int | None
    special_bonus: int
    special_bonus_applied: bool
    movement_value: int | None
    base_roll_available: bool
    special_roll_available: bool
    accent_color: tuple[int, int, int]

    @property
    def roll_available(self) -> bool:
        """Return whether any dice control is currently clickable."""
        return self.base_roll_available or self.special_roll_available


@dataclass(frozen=True, slots=True)
class PlayerHudState:
    """Compact player HUD state near one Yard."""

    player_id: str
    name: str
    color_value: str
    status_text: str
    active: bool
    label_area: ScreenRect
    timer_area: ScreenRect
    seconds_remaining: int | None
    timer_progress: float


@dataclass(frozen=True, slots=True)
class GameplayRenderState:
    """All live gameplay data needed by static renderers."""

    pieces: tuple[PieceRenderGroup, ...]
    dice: DiceHudState
    players: tuple[PlayerHudState, ...]
