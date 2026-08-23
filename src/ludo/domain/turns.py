"""Turn sequencing, dice flow, bonuses, and deterministic timers."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import StrEnum
from random import Random
from typing import Protocol

from ludo.domain.bonus_die import NoSpecialDie, SpecialDie
from ludo.domain.colors import PlayerColor
from ludo.domain.hazards import backward_global_index, backward_relative_progress
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


class MoveActionKind(StrEnum):
    """Selectable movement action categories."""

    FORWARD = "forward"
    BACKWARD_CAPTURE = "backward_capture"


@dataclass(frozen=True, slots=True)
class TurnEvent:
    """Result emitted by a turn-engine operation."""

    kind: TurnEventKind
    player: Player
    dice_value: int | None = None
    special_bonus: int = 0
    approved_movement_value: int | None = None
    special_bonus_applied: bool = False
    legal_piece_ids: tuple[str, ...] = ()
    legal_action_ids: tuple[str, ...] = ()
    moved_piece: Piece | None = None
    collision_outcome: CollisionOutcome | None = None
    bonus_reasons: frozenset[str] = frozenset()
    action_kind: MoveActionKind | None = None
    hazard_triggered: bool = False
    hazard_from: int | None = None
    hazard_to: int | None = None

    @property
    def bonus_granted(self) -> bool:
        """Return whether this event keeps the current player on a bonus roll."""
        return bool(self.bonus_reasons)


@dataclass(frozen=True, slots=True)
class LegalMoveAction:
    """One legal selectable action for the current approved movement value."""

    action_id: str
    piece_id: str
    kind: MoveActionKind
    movement_value: int
    proposal: object


@dataclass(slots=True)
class TurnEngine:
    """Domain turn engine independent from rendering and UI."""

    players: tuple[Player, ...]
    dice: Dice
    clock: Clock
    special_die: SpecialDie = field(default_factory=NoSpecialDie)
    movement_rules: MovementRules = field(default_factory=MovementRules)
    collision_resolver: CollisionResolver = field(default_factory=CollisionResolver)
    hazard_positions: frozenset[int] = frozenset()
    current_player_index: int = 0
    phase: TurnPhase = TurnPhase.WAITING_FOR_ROLL
    last_roll: int | None = None
    last_special_bonus: int = 0
    special_bonus_applied: bool = False
    approved_movement_value: int | None = None
    legal_piece_ids: tuple[str, ...] = ()
    legal_actions: tuple[LegalMoveAction, ...] = ()
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
        self.last_special_bonus = 0
        self.special_bonus_applied = False
        self.approved_movement_value = None
        self.legal_piece_ids = ()
        self.legal_actions = ()
        self.consecutive_sixes = 0
        self._reset_timer()

    def roll(self) -> TurnEvent:
        """Roll dice for the current player and enter move selection when possible."""
        self._require_phase(TurnPhase.WAITING_FOR_ROLL)
        player = self.current_player
        base_roll = self.dice.roll()

        if base_roll == MAX_DICE_VALUE:
            self.consecutive_sixes += 1
        else:
            self.consecutive_sixes = 0

        if self.consecutive_sixes == 3:
            event = TurnEvent(TurnEventKind.TRIPLE_SIX_CANCELLED, player, base_roll)
            self._end_turn()
            return event

        special_bonus = self.special_die.roll_bonus()
        movement_value = base_roll + special_bonus
        legal_actions = self._legal_actions(player, movement_value)
        special_applied = special_bonus > 0
        if not legal_actions and special_bonus:
            fallback_actions = self._legal_actions(player, base_roll)
            if fallback_actions:
                legal_actions = fallback_actions
                movement_value = base_roll
                special_applied = False

        self.last_roll = base_roll
        self.last_special_bonus = special_bonus
        self.special_bonus_applied = special_applied
        self.approved_movement_value = movement_value
        self.legal_actions = legal_actions
        self.legal_piece_ids = tuple(dict.fromkeys(action.piece_id for action in legal_actions))
        if not legal_actions:
            self.phase = TurnPhase.NO_LEGAL_MOVE
            return TurnEvent(
                TurnEventKind.NO_LEGAL_MOVE,
                player,
                base_roll,
                special_bonus=special_bonus,
                approved_movement_value=movement_value,
                special_bonus_applied=special_applied,
            )

        self.phase = TurnPhase.WAITING_FOR_MOVE
        self._reset_timer()
        return TurnEvent(
            TurnEventKind.ROLL_ACCEPTED,
            player,
            base_roll,
            special_bonus=special_bonus,
            approved_movement_value=movement_value,
            special_bonus_applied=special_applied,
            legal_piece_ids=self.legal_piece_ids,
            legal_action_ids=tuple(action.action_id for action in legal_actions),
        )

    def select_piece(self, piece_id: str, action_id: str | None = None) -> TurnEvent:
        """Resolve the selected legal piece for the current dice value."""
        self._require_phase(TurnPhase.WAITING_FOR_MOVE)
        if piece_id not in self.legal_piece_ids:
            msg = "Selected piece is not legal for the current dice value."
            raise ValueError(msg)
        if self.last_roll is None or self.approved_movement_value is None:
            msg = "Cannot select a piece before rolling."
            raise ValueError(msg)

        player = self.current_player
        action = self._select_action(piece_id, action_id)
        proposal = action.proposal

        self._remove_piece_from_occupancies(piece_id)
        collision = self._resolve_action_collision(action)
        self._apply_collision(collision)

        reasons = self._bonus_reasons(self.last_roll, collision)
        event = TurnEvent(
            TurnEventKind.MOVE_RESOLVED,
            player,
            self.last_roll,
            special_bonus=self.last_special_bonus,
            approved_movement_value=action.movement_value,
            special_bonus_applied=self.special_bonus_applied,
            moved_piece=collision.moved_piece,
            collision_outcome=collision,
            bonus_reasons=frozenset(reasons),
            action_kind=action.kind,
            hazard_triggered=(
                action.kind is MoveActionKind.FORWARD
                and proposal.destination.global_outer_index in self.hazard_positions
                and collision.moved_piece.state is PieceState.ON_OUTER_PATH
                and collision.moved_piece.path_progress is not None
                and collision.moved_piece.path_progress
                == backward_relative_progress(
                    collision.moved_piece.owner_color,
                    backward_global_index(proposal.destination.global_outer_index),
                )
            ),
            hazard_from=(
                proposal.destination.global_outer_index
                if action.kind is MoveActionKind.FORWARD
                and proposal.destination.global_outer_index in self.hazard_positions
                else None
            ),
            hazard_to=(
                backward_global_index(proposal.destination.global_outer_index)
                if action.kind is MoveActionKind.FORWARD
                and proposal.destination.global_outer_index in self.hazard_positions
                else None
            ),
        )
        if reasons:
            self.phase = TurnPhase.WAITING_FOR_ROLL
            self.last_roll = None
            self.last_special_bonus = 0
            self.special_bonus_applied = False
            self.approved_movement_value = None
            self.legal_piece_ids = ()
            self.legal_actions = ()
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
        self.last_special_bonus = 0
        self.special_bonus_applied = False
        self.approved_movement_value = None
        self.legal_piece_ids = ()
        self.legal_actions = ()
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

    def _legal_actions(self, player: Player, movement_value: int) -> tuple[LegalMoveAction, ...]:
        actions = []
        for piece in player.pieces:
            forward = self.movement_rules.propose_move(piece, movement_value)
            if forward is not None:
                actions.append(
                    LegalMoveAction(
                        action_id=f"{piece.id}:forward",
                        piece_id=piece.id,
                        kind=MoveActionKind.FORWARD,
                        movement_value=movement_value,
                        proposal=forward,
                    )
                )
            backward = self._backward_capture_action(piece, movement_value)
            if backward is not None:
                actions.append(backward)
        return tuple(actions)

    def _backward_capture_action(
        self, piece: Piece, movement_value: int
    ) -> LegalMoveAction | None:
        proposal = self.movement_rules.propose_backward_outer_capture(piece, movement_value)
        if proposal is None or proposal.destination.global_outer_index is None:
            return None
        occupancy = self.outer_occupancies.get(proposal.destination.global_outer_index)
        if occupancy is None or self.collision_resolver._is_safe(occupancy.global_index):
            return None
        outcome = self.collision_resolver.resolve(proposal, occupancy)
        if not outcome.capture_occurred:
            return None
        return LegalMoveAction(
            action_id=f"{piece.id}:backward_capture",
            piece_id=piece.id,
            kind=MoveActionKind.BACKWARD_CAPTURE,
            movement_value=movement_value,
            proposal=proposal,
        )

    def _select_action(self, piece_id: str, action_id: str | None) -> LegalMoveAction:
        matches = tuple(action for action in self.legal_actions if action.piece_id == piece_id)
        if action_id is not None:
            for action in matches:
                if action.action_id == action_id:
                    return action
            msg = "Selected action is not legal for the current dice value."
            raise ValueError(msg)
        if len(matches) != 1:
            msg = "Selected piece has multiple legal actions; choose an action."
            raise ValueError(msg)
        return matches[0]

    def _resolve_action_collision(self, action: LegalMoveAction) -> CollisionOutcome:
        proposal = action.proposal
        if (
            action.kind is MoveActionKind.FORWARD
            and proposal.destination.global_outer_index in self.hazard_positions
        ):
            return self._resolve_hazard_penalty(proposal)
        occupancy = self._destination_occupancy(proposal)
        return self.collision_resolver.resolve(proposal, occupancy)

    def _resolve_hazard_penalty(self, proposal) -> CollisionOutcome:
        hazard_index = proposal.destination.global_outer_index
        if hazard_index is None:
            return self.collision_resolver.resolve(proposal, None)
        penalty_index = backward_global_index(hazard_index)
        penalty_progress = backward_relative_progress(proposal.piece.owner_color, penalty_index)
        penalty_piece = replace(proposal.piece, path_progress=penalty_progress)
        penalty_proposal = replace(
            proposal,
            piece=penalty_piece,
            destination=proposal.destination.__class__.outer(
                proposal.piece.owner_color,
                penalty_progress,
                penalty_index,
            ),
        )
        return self.collision_resolver.resolve(
            penalty_proposal, self.outer_occupancies.get(penalty_index)
        )

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
