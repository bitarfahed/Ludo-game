"""Special binary bonus-die providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from typing import Protocol

SPECIAL_BONUS_SUCCESS_PROBABILITY = 0.20
SPECIAL_BONUS_VALUE = 2


class SpecialDie(Protocol):
    """Special die provider used after a surviving base roll."""

    def roll_bonus(self) -> int:
        """Return ``0`` for no effect or ``2`` for the movement bonus."""


@dataclass(slots=True)
class FixedSpecialDie:
    """Deterministic special die for tests."""

    bonuses: list[int]

    def roll_bonus(self) -> int:
        """Return the next configured special bonus."""
        if not self.bonuses:
            msg = "FixedSpecialDie has no remaining bonuses."
            raise ValueError(msg)
        bonus = self.bonuses.pop(0)
        _validate_bonus(bonus)
        return bonus


@dataclass(slots=True)
class NoSpecialDie:
    """Special die that deterministically produces no movement bonus."""

    def roll_bonus(self) -> int:
        """Return no special movement bonus."""
        return 0


@dataclass(slots=True)
class RandomSpecialDie:
    """Random special die with injectable generator and configurable probability."""

    random: Random = field(default_factory=Random)
    success_probability: float = SPECIAL_BONUS_SUCCESS_PROBABILITY

    def __post_init__(self) -> None:
        if not 0 <= self.success_probability <= 1:
            msg = "special bonus probability must be between 0 and 1."
            raise ValueError(msg)

    def roll_bonus(self) -> int:
        """Return the special movement bonus according to the configured probability."""
        return SPECIAL_BONUS_VALUE if self.random.random() < self.success_probability else 0


def _validate_bonus(bonus: int) -> None:
    if bonus not in {0, SPECIAL_BONUS_VALUE}:
        msg = f"special bonus must be 0 or {SPECIAL_BONUS_VALUE}."
        raise ValueError(msg)
