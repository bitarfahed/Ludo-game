"""Hazard-square placement and penalty helpers."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from random import Random
from typing import Protocol, TypeVar

from ludo.domain.board import OUTER_PATH_LENGTH, BoardTopology
from ludo.domain.colors import PlayerColor

HAZARD_COUNT = 4
HAZARD_PENALTY_STEPS = 2
SECTOR_LENGTH = OUTER_PATH_LENGTH // HAZARD_COUNT

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
        if not self.choices:
            msg = "FixedHazardRandomizer has no remaining choices."
            raise ValueError(msg)
        choice = self.choices.pop(0)
        if choice not in values:
            msg = "Fixed hazard choice is not available."
            raise ValueError(msg)
        return choice


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
    """Generate one non-safe hazard in each board sector."""
    chooser = randomizer or RandomHazardRandomizer()
    board = topology or BoardTopology()
    hazards = []
    for sector in range(HAZARD_COUNT):
        start = sector * SECTOR_LENGTH
        end = start + SECTOR_LENGTH
        candidates = tuple(
            index for index in range(start, end) if not board.is_safe_outer_position(index)
        )
        hazards.append(chooser.choice(candidates))
    return frozenset(hazards)


def backward_global_index(global_index: int, steps: int = HAZARD_PENALTY_STEPS) -> int:
    """Return a global outer index moved backward by ``steps`` with wraparound."""
    return (global_index - steps) % OUTER_PATH_LENGTH


def backward_relative_progress(color: PlayerColor, global_index: int) -> int:
    """Return color-relative progress for a global outer index."""
    return (global_index - BoardTopology().start_position(color)) % OUTER_PATH_LENGTH
