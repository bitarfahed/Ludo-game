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
class PieceRenderGroup:
    """Pieces sharing one render location."""

    center: tuple[int, int]
    bounds: ScreenRect
    pieces: tuple[PieceRenderItem, ...]
    placeholder_label: str | None = None

    @property
    def is_stack_placeholder(self) -> bool:
        """Return whether this group should draw a compact placeholder."""
        return self.placeholder_label is not None


@dataclass(frozen=True, slots=True)
class DiceHudState:
    """Center dice display state."""

    bounds: ScreenRect
    current_value: int | None
    roll_available: bool
    accent_color: tuple[int, int, int]


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
