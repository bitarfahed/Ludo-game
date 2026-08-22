"""Logical one-dimensional Ludo board topology."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from ludo.domain.colors import PlayerColor

OUTER_PATH_LENGTH = 52
HOME_PATH_LENGTH = 5

DEFAULT_START_POSITIONS: Mapping[PlayerColor, int] = MappingProxyType(
    {
        PlayerColor.RED: 0,
        PlayerColor.GREEN: 13,
        PlayerColor.YELLOW: 26,
        PlayerColor.BLUE: 39,
    }
)
DEFAULT_STAR_SAFE_POSITIONS = frozenset({8, 21, 34, 47})


@dataclass(frozen=True, slots=True)
class HomePathPosition:
    """A private Home-Path square for one color."""

    color: PlayerColor
    index: int

    def __post_init__(self) -> None:
        _require_player_color(self.color)
        if not 0 <= self.index < HOME_PATH_LENGTH:
            msg = f"Home-Path index must be between 0 and {HOME_PATH_LENGTH - 1}."
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class FinishedDestination:
    """The separate destination after a color's five Home-Path squares."""

    color: PlayerColor

    def __post_init__(self) -> None:
        _require_player_color(self.color)


@dataclass(frozen=True, slots=True)
class BoardTopology:
    """Immutable logical board description independent from screen coordinates."""

    start_positions: Mapping[PlayerColor, int] = field(
        default_factory=lambda: DEFAULT_START_POSITIONS
    )
    star_safe_positions: frozenset[int] = DEFAULT_STAR_SAFE_POSITIONS

    def __post_init__(self) -> None:
        normalized_starts = dict(self.start_positions)
        normalized_stars = frozenset(self.star_safe_positions)
        self._validate_start_positions(normalized_starts)
        self._validate_safe_positions(normalized_starts, normalized_stars)

        object.__setattr__(self, "start_positions", MappingProxyType(normalized_starts))
        object.__setattr__(self, "star_safe_positions", normalized_stars)

    @property
    def outer_positions(self) -> tuple[int, ...]:
        """Return all shared outer-path global indices."""
        return tuple(range(OUTER_PATH_LENGTH))

    @property
    def safe_outer_positions(self) -> frozenset[int]:
        """Return all non-capturing shared outer-path indices."""
        return frozenset(self.start_positions.values()) | self.star_safe_positions

    def start_position(self, color: PlayerColor) -> int:
        """Return the global outer-path start index for a color."""
        _require_player_color(color)
        return self.start_positions[color]

    def is_safe_outer_position(self, global_index: int) -> bool:
        """Return whether a global outer-path index is safe."""
        self._require_global_outer_index(global_index)
        return global_index in self.safe_outer_positions

    def global_outer_index(self, color: PlayerColor, relative_progress: int) -> int:
        """Map player-relative outer progress to the shared global outer-path index."""
        _require_player_color(color)
        self._require_relative_outer_progress(relative_progress)
        return (self.start_position(color) + relative_progress) % OUTER_PATH_LENGTH

    def home_path(self, color: PlayerColor) -> tuple[HomePathPosition, ...]:
        """Return the five private Home-Path positions for a color."""
        _require_player_color(color)
        return tuple(
            HomePathPosition(color=color, index=index) for index in range(HOME_PATH_LENGTH)
        )

    def finished_destination(self, color: PlayerColor) -> FinishedDestination:
        """Return the separate Finished destination for a color."""
        _require_player_color(color)
        return FinishedDestination(color=color)

    @staticmethod
    def _require_relative_outer_progress(relative_progress: int) -> None:
        if not 0 <= relative_progress < OUTER_PATH_LENGTH:
            msg = f"relative outer progress must be between 0 and {OUTER_PATH_LENGTH - 1}."
            raise ValueError(msg)

    @staticmethod
    def _require_global_outer_index(global_index: int) -> None:
        if not 0 <= global_index < OUTER_PATH_LENGTH:
            msg = f"global outer index must be between 0 and {OUTER_PATH_LENGTH - 1}."
            raise ValueError(msg)

    @staticmethod
    def _validate_start_positions(start_positions: Mapping[PlayerColor, int]) -> None:
        if set(start_positions) != set(PlayerColor):
            msg = "Board topology requires exactly one start position for each PlayerColor."
            raise ValueError(msg)
        if len(set(start_positions.values())) != len(PlayerColor):
            msg = "Player start positions must be unique."
            raise ValueError(msg)
        for color, index in start_positions.items():
            _require_player_color(color)
            BoardTopology._require_global_outer_index(index)

    @staticmethod
    def _validate_safe_positions(
        start_positions: Mapping[PlayerColor, int], star_safe_positions: frozenset[int]
    ) -> None:
        for index in star_safe_positions:
            BoardTopology._require_global_outer_index(index)
        safe_positions = frozenset(start_positions.values()) | star_safe_positions
        if len(safe_positions) != 8:
            msg = "Board topology requires exactly 8 safe outer positions."
            raise ValueError(msg)

def _require_player_color(color: PlayerColor) -> None:
    if not isinstance(color, PlayerColor):
        msg = "Expected a PlayerColor."
        raise TypeError(msg)
