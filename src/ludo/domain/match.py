"""Match setup, active-player eligibility, ranking, and completion."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from random import Random
from typing import Protocol, TypeVar

from ludo.domain.colors import PlayerColor
from ludo.domain.pieces import PieceState
from ludo.domain.players import Player
from ludo.domain.turns import Clock, Dice, FixedClock, RandomDice, TurnEngine

MIN_PLAYERS = 2
MAX_PLAYERS = 4
CLOCKWISE_COLORS = (
    PlayerColor.RED,
    PlayerColor.GREEN,
    PlayerColor.YELLOW,
    PlayerColor.BLUE,
)
OPPOSITE_COLOR_PAIRS = (
    (PlayerColor.RED, PlayerColor.YELLOW),
    (PlayerColor.GREEN, PlayerColor.BLUE),
)

T = TypeVar("T")


class ColorRandomizer(Protocol):
    """Random source used for deterministic color assignment tests."""

    def choice(self, values: Sequence[T]) -> T:
        """Choose one value."""

    def sample(self, values: Sequence[T], count: int) -> tuple[T, ...]:
        """Choose ``count`` distinct values."""


@dataclass(slots=True)
class FixedColorRandomizer:
    """Deterministic color randomizer for tests."""

    choices: list = field(default_factory=list)
    samples: list[tuple] = field(default_factory=list)

    def choice(self, values: Sequence[T]) -> T:
        """Return the next fixed choice."""
        if not self.choices:
            msg = "FixedColorRandomizer has no remaining choices."
            raise ValueError(msg)
        choice = self.choices.pop(0)
        if choice not in values:
            msg = "Fixed choice is not available."
            raise ValueError(msg)
        return choice

    def sample(self, values: Sequence[T], count: int) -> tuple[T, ...]:
        """Return the next fixed sample."""
        if not self.samples:
            msg = "FixedColorRandomizer has no remaining samples."
            raise ValueError(msg)
        sample = self.samples.pop(0)
        if len(sample) != count or len(set(sample)) != count or not set(sample).issubset(values):
            msg = "Fixed sample must contain the requested distinct available values."
            raise ValueError(msg)
        return sample


@dataclass(slots=True)
class RandomColorRandomizer:
    """Random color assignment source with injectable random generator."""

    random: Random = field(default_factory=Random)

    def choice(self, values: Sequence[T]) -> T:
        """Choose one value randomly."""
        return self.random.choice(tuple(values))

    def sample(self, values: Sequence[T], count: int) -> tuple[T, ...]:
        """Choose distinct values randomly."""
        return tuple(self.random.sample(tuple(values), count))


@dataclass(frozen=True, slots=True)
class RankingEntry:
    """A permanent match ranking for one player."""

    rank: int
    player: Player


@dataclass(slots=True)
class Match:
    """Match-level state for setup, eligibility, rankings, and completion."""

    players: tuple[Player, ...]
    turn_engine: TurnEngine
    inactive_colors: frozenset[PlayerColor]
    rankings: tuple[RankingEntry, ...] = ()
    is_complete: bool = False

    @classmethod
    def create(
        cls,
        player_names: tuple[str, ...],
        color_randomizer: ColorRandomizer | None = None,
        dice: Dice | None = None,
        clock: Clock | None = None,
    ) -> Match:
        """Create a validated match with random color assignment."""
        player_count = len(player_names)
        if player_count < MIN_PLAYERS or player_count > MAX_PLAYERS:
            msg = "Match requires 2, 3, or 4 players."
            raise ValueError(msg)

        randomizer = color_randomizer or RandomColorRandomizer()
        assigned_colors = _assign_colors(player_count, randomizer)
        players_by_color = {
            color: Player(id=f"player-{index}", name=name, color=color)
            for index, (name, color) in enumerate(
                zip(player_names, assigned_colors, strict=True), start=1
            )
        }
        ordered_players = tuple(
            players_by_color[color] for color in CLOCKWISE_COLORS if color in players_by_color
        )
        inactive_colors = frozenset(set(PlayerColor) - set(players_by_color))
        engine = TurnEngine(
            players=ordered_players,
            dice=dice or RandomDice(),
            clock=clock or FixedClock(),
        )
        return cls(ordered_players, engine, inactive_colors)

    @property
    def final_standings(self) -> tuple[RankingEntry, ...]:
        """Return final standings in rank order."""
        return tuple(sorted(self.rankings, key=lambda entry: entry.rank))

    def player_by_color(self, color: PlayerColor) -> Player:
        """Return an active or ranked player by color."""
        ranked_players = tuple(entry.player for entry in self.rankings)
        for active_player in (*self.turn_engine.players, *ranked_players):
            if active_player.color is color:
                return active_player
        msg = f"No match player uses color {color}."
        raise ValueError(msg)

    def evaluate_rankings(self) -> tuple[RankingEntry, ...]:
        """Assign newly completed ranks and auto-complete the final remaining player."""
        if self.is_complete:
            return self.rankings

        for active_player in tuple(self.turn_engine.players):
            if self._is_ranked(active_player) or not _has_finished_all_pieces(active_player):
                continue
            self._rank_player(active_player)

        if len(self.turn_engine.players) == 1 and not self.is_complete:
            self._rank_player(self.turn_engine.players[0])
            self.is_complete = True

        return self.rankings

    def _rank_player(self, player: Player) -> None:
        if self._is_ranked(player):
            return
        entry = RankingEntry(rank=len(self.rankings) + 1, player=player)
        self.rankings = (*self.rankings, entry)
        self.turn_engine.remove_player(player.id)
        self.players = tuple(
            active_player for active_player in self.players if active_player.id != player.id
        )

    def _is_ranked(self, player: Player) -> bool:
        return any(entry.player.id == player.id for entry in self.rankings)


def _assign_colors(player_count: int, randomizer: ColorRandomizer) -> tuple[PlayerColor, ...]:
    if player_count == 2:
        opposite_pair = randomizer.choice(OPPOSITE_COLOR_PAIRS)
        return randomizer.sample(opposite_pair, 2)
    return randomizer.sample(CLOCKWISE_COLORS, player_count)


def _has_finished_all_pieces(player: Player) -> bool:
    return all(piece.state is PieceState.FINISHED for piece in player.pieces)
