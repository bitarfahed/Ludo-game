"""Hazard-square placement and penalty helpers."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from random import Random
from typing import Protocol, TypeVar

from ludo.domain.board import OUTER_PATH_LENGTH, BoardTopology
from ludo.domain.colors import PlayerColor

SECTOR_COUNT = 4
HAZARD_COUNT = 8
BOOST_COUNT = 4
SHIELD_SQUARE_COUNT = 4
HAZARD_PENALTY_STEPS = 2
BOOST_STEPS = 2
SECTOR_LENGTH = OUTER_PATH_LENGTH // SECTOR_COUNT

T = TypeVar("T")


class HazardRandomizer(Protocol):
    """Random source used to choose fixed match hazards."""

    def choice(self, values: Sequence[T]) -> T:
        """Choose one value."""


@dataclass(slots=True)
class FixedHazardRandomizer:
    """Deterministic hazard chooser for tests."""

    choices: list[int]

    def choice(self, values: Sequence[T]) -> T:
        """Return the next configured hazard index."""
        while self.choices:
            choice = self.choices.pop(0)
            if choice in values:
                return choice
        if not values:
            msg = "Fixed hazard choice is not available."
            raise ValueError(msg)
        return values[0]


@dataclass(frozen=True, slots=True)
class SpecialSquareLayout:
    """Fixed match special-square positions on the shared outer path."""

    hazards: frozenset[int]
    boosts: frozenset[int]
    shields: frozenset[int]

    @property
    def all_positions(self) -> frozenset[int]:
        """Return every special-square position."""
        return self.hazards | self.boosts | self.shields


@dataclass(slots=True)
class RandomHazardRandomizer:
    """Random hazard chooser with injectable generator."""

    random: Random = field(default_factory=Random)

    def choice(self, values: Sequence[T]) -> T:
        """Choose one hazard index randomly."""
        return self.random.choice(tuple(values))


def generate_hazards(
    randomizer: HazardRandomizer | None = None,
    topology: BoardTopology | None = None,
) -> frozenset[int]:
    """Generate eight non-safe hazards, two in each board sector."""
    return generate_special_squares(randomizer, topology).hazards


def generate_special_squares(
    randomizer: HazardRandomizer | None = None,
    topology: BoardTopology | None = None,
) -> SpecialSquareLayout:
    """Generate hazards, boosts, and shield squares with fixed per-sector distribution."""
    chooser = randomizer or RandomHazardRandomizer()
    board = topology or BoardTopology()
    hazards: list[int] = []
    boosts: list[int] = []
    shields: list[int] = []
    for sector in range(SECTOR_COUNT):
        start = sector * SECTOR_LENGTH
        end = start + SECTOR_LENGTH
        candidates = [
            index for index in range(start, end) if not board.is_safe_outer_position(index)
        ]
        for target in (hazards, hazards, boosts, shields):
            choice = chooser.choice(tuple(candidates))
            target.append(choice)
            candidates.remove(choice)
    return SpecialSquareLayout(
        hazards=frozenset(hazards),
        boosts=frozenset(boosts),
        shields=frozenset(shields),
    )


def backward_global_index(global_index: int, steps: int = HAZARD_PENALTY_STEPS) -> int:
    """Return a global outer index moved backward by ``steps`` with wraparound."""
    return (global_index - steps) % OUTER_PATH_LENGTH


def forward_global_index(global_index: int, steps: int = BOOST_STEPS) -> int:
    """Return a global outer index moved forward by ``steps`` with wraparound."""
    return (global_index + steps) % OUTER_PATH_LENGTH


def backward_relative_progress(color: PlayerColor, global_index: int) -> int:
    """Return color-relative progress for a global outer index."""
    return (global_index - BoardTopology().start_position(color)) % OUTER_PATH_LENGTH
