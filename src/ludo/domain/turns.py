"""Turn sequencing, dice flow, bonuses, and deterministic timers."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import StrEnum
from random import Random
from typing import Protocol

from ludo.domain.colors import PlayerColor
from ludo.domain.movement import MAX_DICE_VALUE, MIN_DICE_VALUE, MovementRules
from ludo.domain.occupancy import CollisionOutcome, CollisionResolver, OuterPathOccupancy
from ludo.domain.pieces import Piece, PieceState
from ludo.domain.players import Player

DECISION_TIMEOUT_SECONDS = 10


class Dice(Protocol):
    """Dice provider abstraction used by deterministic tests and future production play."""

    def roll(self) -> int:
        """Return one dice value."""


class Clock(Protocol):
    """Clock abstraction for deterministic timeout behavior."""

    def now(self) -> float:
        """Return current monotonic time in seconds."""


@dataclass(slots=True)
class FixedDice:
    """Deterministic dice provider that returns predefined values."""

    values: list[int]

    def roll(self) -> int:
        """Return the next configured dice value."""
        if not self.values:
            msg = "FixedDice has no remaining values."
            raise ValueError(msg)
        value = self.values.pop(0)
        _validate_dice_value(value)
        return value


@dataclass(slots=True)
class RandomDice:
    """Random dice provider with injectable random generator."""

    random: Random = field(default_factory=Random)

    def roll(self) -> int:
        """Return a random dice value from 1 through 6."""
        return self.random.randint(MIN_DICE_VALUE, MAX_DICE_VALUE)


@dataclass(slots=True)
class FixedClock:
    """Mutable deterministic clock for tests."""

    current_time: float = 0

    def now(self) -> float:
        """Return the current fake time."""
        return self.current_time

    def advance(self, seconds: float) -> None:
        """Move fake time forward."""
        if seconds < 0:
            msg = "Clock cannot advance by a negative duration."
            raise ValueError(msg)
        self.current_time += seconds


class TurnPhase(StrEnum):
    """Current turn decision phase."""

    WAITING_FOR_ROLL = "waiting_for_roll"
    WAITING_FOR_MOVE = "waiting_for_move"
    NO_LEGAL_MOVE = "no_legal_move"


class TurnEventKind(StrEnum):
    """Inspectable turn-engine event categories."""

    ROLL_ACCEPTED = "roll_accepted"
    MOVE_RESOLVED = "move_resolved"
    NO_LEGAL_MOVE = "no_legal_move"
    TRIPLE_SIX_CANCELLED = "triple_six_cancelled"
    ROLL_TIMEOUT = "roll_timeout"
    MOVE_TIMEOUT = "move_timeout"
    TURN_PASSED = "turn_passed"


@dataclass(frozen=True, slots=True)
class TurnEvent:
    """Result emitted by a turn-engine operation."""

    kind: TurnEventKind
    player: Player
    dice_value: int | None = None
    legal_piece_ids: tuple[str, ...] = ()
    moved_piece: Piece | None = None
    collision_outcome: CollisionOutcome | None = None
    bonus_reasons: frozenset[str] = frozenset()

    @property
    def bonus_granted(self) -> bool:
        """Return whether this event keeps the current player on a bonus roll."""
        return bool(self.bonus_reasons)


@dataclass(slots=True)
class TurnEngine:
    """Domain turn engine independent from rendering and UI."""

    players: tuple[Player, ...]
    dice: Dice
    clock: Clock
    movement_rules: MovementRules = field(default_factory=MovementRules)
    collision_resolver: CollisionResolver = field(default_factory=CollisionResolver)
    current_player_index: int = 0
    phase: TurnPhase = TurnPhase.WAITING_FOR_ROLL
    last_roll: int | None = None
    legal_piece_ids: tuple[str, ...] = ()
    consecutive_sixes: int = 0
    outer_occupancies: dict[int, OuterPathOccupancy] = field(default_factory=dict)
    _deadline: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.players:
            msg = "TurnEngine requires at least one active player."
            raise ValueError(msg)
        self._deadline = self.clock.now() + DECISION_TIMEOUT_SECONDS

    @property
    def current_player(self) -> Player:
        """Return the player whose decision is currently active."""
        return self.players[self.current_player_index]

    @property
    def seconds_remaining(self) -> int:
        """Return whole seconds remaining in the current decision window."""
        return max(0, int(self._deadline - self.clock.now()))

    def player_by_color(self, color: PlayerColor) -> Player:
        """Return an active player by color."""
        for active_player in self.players:
            if active_player.color is color:
                return active_player
        msg = f"No active player uses color {color}."
        raise ValueError(msg)

    def set_occupancy(self, occupancy: OuterPathOccupancy) -> None:
        """Set one outer-path occupancy for tests or future game-state integration."""
        self.outer_occupancies[occupancy.global_index] = occupancy

    def replace_player(self, updated_player: Player) -> None:
        """Replace an active player while preserving their turn position."""
        for index, active_player in enumerate(self.players):
            if active_player.id == updated_player.id:
                self.players = (
                    *self.players[:index],
                    updated_player,
                    *self.players[index + 1 :],
                )
                return
        msg = f"Cannot replace inactive player {updated_player.id}."
        raise ValueError(msg)

    def remove_player(self, player_id: str) -> None:
        """Remove a ranked player from future turn rotation."""
        remaining = tuple(player for player in self.players if player.id != player_id)
        if len(remaining) == len(self.players):
            msg = f"Cannot remove inactive player {player_id}."
            raise ValueError(msg)
        self.players = remaining
        if not self.players or self.current_player_index >= len(self.players):
            self.current_player_index = 0
        self.phase = TurnPhase.WAITING_FOR_ROLL
        self.last_roll = None
        self.legal_piece_ids = ()
        self.consecutive_sixes = 0
        self._reset_timer()

    def roll(self) -> TurnEvent:
        """Roll dice for the current player and enter move selection when possible."""
        self._require_phase(TurnPhase.WAITING_FOR_ROLL)
        player = self.current_player
        dice_value = self.dice.roll()

        if dice_value == MAX_DICE_VALUE:
            self.consecutive_sixes += 1
        else:
            self.consecutive_sixes = 0

        if self.consecutive_sixes == 3:
            event = TurnEvent(TurnEventKind.TRIPLE_SIX_CANCELLED, player, dice_value)
            self._end_turn()
            return event

        legal_pieces = self.movement_rules.legal_pieces(player, dice_value)
        self.last_roll = dice_value
        self.legal_piece_ids = tuple(piece.id for piece in legal_pieces)
        if not legal_pieces:
            self.phase = TurnPhase.NO_LEGAL_MOVE
            return TurnEvent(TurnEventKind.NO_LEGAL_MOVE, player, dice_value)

        self.phase = TurnPhase.WAITING_FOR_MOVE
        self._reset_timer()
        return TurnEvent(
            TurnEventKind.ROLL_ACCEPTED, player, dice_value, legal_piece_ids=self.legal_piece_ids
        )

    def select_piece(self, piece_id: str) -> TurnEvent:
        """Resolve the selected legal piece for the current dice value."""
        self._require_phase(TurnPhase.WAITING_FOR_MOVE)
        if piece_id not in self.legal_piece_ids:
            msg = "Selected piece is not legal for the current dice value."
            raise ValueError(msg)
        if self.last_roll is None:
            msg = "Cannot select a piece before rolling."
            raise ValueError(msg)

        player = self.current_player
        piece = self._piece_by_id(player, piece_id)
        proposal = self.movement_rules.propose_move(piece, self.last_roll)
        if proposal is None:
            msg = "Selected piece no longer has a legal move."
            raise ValueError(msg)

        self._remove_piece_from_occupancies(piece.id)
        occupancy = self._destination_occupancy(proposal)
        collision = self.collision_resolver.resolve(proposal, occupancy)
        self._apply_collision(collision)

        reasons = self._bonus_reasons(self.last_roll, collision)
        event = TurnEvent(
            TurnEventKind.MOVE_RESOLVED,
            player,
            self.last_roll,
            moved_piece=collision.moved_piece,
            collision_outcome=collision,
            bonus_reasons=frozenset(reasons),
        )
        if reasons:
            self.phase = TurnPhase.WAITING_FOR_ROLL
            self.last_roll = None
            self.legal_piece_ids = ()
            self._reset_timer()
        else:
            self._end_turn()
        return event

    def complete_no_legal_move_notice(self) -> TurnEvent:
        """Finish no-legal-move handling and pass the turn."""
        self._require_phase(TurnPhase.NO_LEGAL_MOVE)
        player = self.current_player
        dice_value = self.last_roll
        self._end_turn()
        return TurnEvent(TurnEventKind.TURN_PASSED, player, dice_value)

    def expire_decision_if_needed(self) -> TurnEvent | None:
        """Expire the active decision window if the injected clock reached its deadline."""
        if self.clock.now() < self._deadline:
            return None
        player = self.current_player
        if self.phase is TurnPhase.WAITING_FOR_ROLL:
            self._end_turn()
            return TurnEvent(TurnEventKind.ROLL_TIMEOUT, player)
        if self.phase is TurnPhase.WAITING_FOR_MOVE:
            dice_value = self.last_roll
            self._end_turn()
            return TurnEvent(TurnEventKind.MOVE_TIMEOUT, player, dice_value)
        return None

    def _end_turn(self) -> None:
        if not self.players:
            return
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.phase = TurnPhase.WAITING_FOR_ROLL
        self.last_roll = None
        self.legal_piece_ids = ()
        self.consecutive_sixes = 0
        self._reset_timer()

    def _reset_timer(self) -> None:
        self._deadline = self.clock.now() + DECISION_TIMEOUT_SECONDS

    def _require_phase(self, expected_phase: TurnPhase) -> None:
        if self.phase is not expected_phase:
            msg = f"Expected phase {expected_phase}, got {self.phase}."
            raise ValueError(msg)

    @staticmethod
    def _piece_by_id(player: Player, piece_id: str) -> Piece:
        for piece in player.pieces:
            if piece.id == piece_id:
                return piece
        msg = f"Player does not own piece {piece_id}."
        raise ValueError(msg)

    def _apply_collision(self, collision: CollisionOutcome) -> None:
        self._replace_piece(collision.moved_piece)
        if collision.captured_piece is not None:
            self._replace_piece(collision.captured_piece)
        if collision.destination_occupancy is not None:
            self.outer_occupancies[
                collision.destination_occupancy.global_index
            ] = collision.destination_occupancy

    def _replace_piece(self, updated_piece: Piece) -> None:
        for player_index, active_player in enumerate(self.players):
            pieces = tuple(
                updated_piece if piece.id == updated_piece.id else piece
                for piece in active_player.pieces
            )
            if pieces != active_player.pieces:
                self.players = (
                    *self.players[:player_index],
                    replace(active_player, pieces=pieces),
                    *self.players[player_index + 1 :],
                )
                return

    def _remove_piece_from_occupancies(self, piece_id: str) -> None:
        for index, occupancy in tuple(self.outer_occupancies.items()):
            remaining = tuple(piece for piece in occupancy.pieces if piece.id != piece_id)
            if len(remaining) == len(occupancy.pieces):
                continue
            if remaining:
                self.outer_occupancies[index] = OuterPathOccupancy(
                    index, remaining, occupancy.was_protected
                )
            else:
                del self.outer_occupancies[index]

    def _destination_occupancy(self, proposal) -> OuterPathOccupancy | None:
        destination_index = proposal.destination.global_outer_index
        if destination_index is None:
            return None
        return self.outer_occupancies.get(destination_index)

    @staticmethod
    def _bonus_reasons(dice_value: int, collision: CollisionOutcome) -> set[str]:
        reasons: set[str] = set()
        if dice_value == MAX_DICE_VALUE:
            reasons.add("rolled_6")
        if collision.capture_occurred:
            reasons.add("capture")
        if collision.moved_piece.state is PieceState.FINISHED:
            reasons.add("finish")
        return reasons


def _validate_dice_value(value: int) -> None:
    if not MIN_DICE_VALUE <= value <= MAX_DICE_VALUE:
        msg = f"dice value must be between {MIN_DICE_VALUE} and {MAX_DICE_VALUE}."
        raise ValueError(msg)
