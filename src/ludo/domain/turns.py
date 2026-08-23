"""Turn sequencing, dice flow, bonuses, and deterministic timers."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import StrEnum
from random import Random
from typing import Protocol

from ludo.domain.bonus_die import NoSpecialDie, SpecialDie
from ludo.domain.colors import PlayerColor
from ludo.domain.hazards import (
    backward_global_index,
    backward_relative_progress,
    forward_global_index,
)
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
    WAITING_FOR_SPECIAL_ROLL = "waiting_for_special_roll"
    WAITING_FOR_MOVE = "waiting_for_move"
    NO_LEGAL_MOVE = "no_legal_move"


class TurnEventKind(StrEnum):
    """Inspectable turn-engine event categories."""

    ROLL_ACCEPTED = "roll_accepted"
    BASE_ROLL_ACCEPTED = "base_roll_accepted"
    SPECIAL_ROLL_ACCEPTED = "special_roll_accepted"
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
    boost_triggered: bool = False
    boost_from: int | None = None
    boost_to: int | None = None
    shield_acquired: bool = False
    shield_broken: bool = False

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
    boost_positions: frozenset[int] = frozenset()
    shield_square_positions: frozenset[int] = frozenset()
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
    forced_six_player_ids: frozenset[str] = frozenset()
    _deadline: float = field(init=False, repr=False)
    _turn_started_all_yard: bool = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.players:
            msg = "TurnEngine requires at least one active player."
            raise ValueError(msg)
        self._deadline = self.clock.now() + DECISION_TIMEOUT_SECONDS
        self._turn_started_all_yard = self._all_pieces_in_yard(self.current_player)

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
        self._turn_started_all_yard = (
            self._all_pieces_in_yard(self.current_player) if self.players else False
        )

    def roll(self) -> TurnEvent:
        """Roll the normal die and wait for the explicit special die roll."""
        self._require_phase(TurnPhase.WAITING_FOR_ROLL)
        player = self.current_player
        base_roll = (
            MAX_DICE_VALUE if player.id in self.forced_six_player_ids else self.dice.roll()
        )
        self.forced_six_player_ids = frozenset(
            player_id for player_id in self.forced_six_player_ids if player_id != player.id
        )

        if base_roll == MAX_DICE_VALUE:
            self.consecutive_sixes += 1
        else:
            self.consecutive_sixes = 0

        if self.consecutive_sixes == 3:
            event = TurnEvent(TurnEventKind.TRIPLE_SIX_CANCELLED, player, base_roll)
            self._end_turn()
            return event

        self.last_roll = base_roll
        self.last_special_bonus = 0
        self.special_bonus_applied = False
        self.approved_movement_value = None
        self.legal_actions = ()
        self.legal_piece_ids = ()
        self.phase = TurnPhase.WAITING_FOR_SPECIAL_ROLL
        self._reset_timer()
        return TurnEvent(TurnEventKind.BASE_ROLL_ACCEPTED, player, base_roll)

    def roll_special(self) -> TurnEvent:
        """Roll the special die and construct explicit legal movement choices."""
        self._require_phase(TurnPhase.WAITING_FOR_SPECIAL_ROLL)
        player = self.current_player
        if self.last_roll is None:
            msg = "Cannot roll special die before the normal die."
            raise ValueError(msg)

        base_roll = self.last_roll
        special_bonus = self.special_die.roll_bonus()
        legal_actions = self._legal_actions_for_roll(player, base_roll, special_bonus)
        special_applied = special_bonus > 0
        movement_value = base_roll + special_bonus if special_applied else base_roll

        self.last_special_bonus = special_bonus
        self.special_bonus_applied = special_applied and any(
            action.movement_value == base_roll + special_bonus for action in legal_actions
        )
        self.approved_movement_value = None
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
                special_bonus_applied=False,
            )

        self.phase = TurnPhase.WAITING_FOR_MOVE
        self._reset_timer()
        return TurnEvent(
            TurnEventKind.SPECIAL_ROLL_ACCEPTED,
            player,
            base_roll,
            special_bonus=special_bonus,
            approved_movement_value=None,
            special_bonus_applied=self.special_bonus_applied,
            legal_piece_ids=self.legal_piece_ids,
            legal_action_ids=tuple(action.action_id for action in legal_actions),
        )

    def select_piece(self, piece_id: str, action_id: str | None = None) -> TurnEvent:
        """Resolve the selected legal piece for the current dice value."""
        self._require_phase(TurnPhase.WAITING_FOR_MOVE)
        if piece_id not in self.legal_piece_ids:
            msg = "Selected piece is not legal for the current dice value."
            raise ValueError(msg)
        if self.last_roll is None:
            msg = "Cannot select a piece before rolling."
            raise ValueError(msg)

        player = self.current_player
        action = self._select_action(piece_id, action_id)
        proposal = action.proposal

        self._remove_piece_from_occupancies(piece_id)
        collision = self._resolve_action_collision(action)
        self._apply_collision(collision)
        landing_index = proposal.destination.global_outer_index
        hazard_triggered = (
            action.kind is MoveActionKind.FORWARD and landing_index in self.hazard_positions
        )
        boost_triggered = (
            action.kind is MoveActionKind.FORWARD and landing_index in self.boost_positions
        )
        shield_acquired = (
            action.kind is MoveActionKind.FORWARD
            and landing_index in self.shield_square_positions
            and not proposal.piece.has_shield
            and collision.moved_piece.has_shield
        )

        reasons = self._bonus_reasons(self.last_roll, collision)
        event = TurnEvent(
            TurnEventKind.MOVE_RESOLVED,
            player,
            self.last_roll,
            special_bonus=self.last_special_bonus,
            approved_movement_value=action.movement_value,
            special_bonus_applied=action.movement_value != self.last_roll,
            moved_piece=collision.moved_piece,
            collision_outcome=collision,
            bonus_reasons=frozenset(reasons),
            action_kind=action.kind,
            hazard_triggered=hazard_triggered,
            hazard_from=landing_index if hazard_triggered else None,
            hazard_to=backward_global_index(landing_index) if hazard_triggered else None,
            boost_triggered=boost_triggered,
            boost_from=landing_index if boost_triggered else None,
            boost_to=forward_global_index(landing_index) if boost_triggered else None,
            shield_acquired=shield_acquired,
            shield_broken=collision.shield_broken_piece is not None,
        )
        if reasons:
            self.phase = TurnPhase.WAITING_FOR_ROLL
            self.last_roll = None
            self.last_special_bonus = 0
            self.special_bonus_applied = False
            self.approved_movement_value = None
            self.legal_piece_ids = ()
            self.legal_actions = ()
            self._turn_started_all_yard = self._all_pieces_in_yard(self.current_player)
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
        if self.phase is TurnPhase.WAITING_FOR_SPECIAL_ROLL:
            dice_value = self.last_roll
            self._end_turn()
            return TurnEvent(TurnEventKind.ROLL_TIMEOUT, player, dice_value)
        if self.phase is TurnPhase.WAITING_FOR_MOVE:
            dice_value = self.last_roll
            self._end_turn()
            return TurnEvent(TurnEventKind.MOVE_TIMEOUT, player, dice_value)
        return None

    def _end_turn(self) -> None:
        if not self.players:
            return
        ending_player = self.current_player
        if self._turn_started_all_yard and self._all_pieces_in_yard(ending_player):
            self.forced_six_player_ids = frozenset((*self.forced_six_player_ids, ending_player.id))
        elif not self._all_pieces_in_yard(ending_player):
            self.forced_six_player_ids = frozenset(
                player_id
                for player_id in self.forced_six_player_ids
                if player_id != ending_player.id
            )
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
        self._turn_started_all_yard = self._all_pieces_in_yard(self.current_player)

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
        if collision.shield_broken_piece is not None:
            self._replace_piece(collision.shield_broken_piece)
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

    def _legal_actions_for_roll(
        self, player: Player, base_roll: int, special_bonus: int
    ) -> tuple[LegalMoveAction, ...]:
        actions = list(self._legal_actions(player, base_roll, base_roll=base_roll))
        if special_bonus <= 0:
            return tuple(actions)
        bonus_value = base_roll + special_bonus
        actions.extend(self._legal_actions(player, bonus_value, base_roll=base_roll))
        return tuple(actions)

    def _legal_actions(
        self, player: Player, movement_value: int, *, base_roll: int
    ) -> tuple[LegalMoveAction, ...]:
        actions = []
        for piece in player.pieces:
            forward = None
            if piece.state is PieceState.IN_YARD and movement_value != base_roll:
                forward = None
            elif piece.state is not PieceState.IN_YARD or base_roll == MAX_DICE_VALUE:
                yard_movement = base_roll if piece.state is PieceState.IN_YARD else movement_value
                forward = self.movement_rules.propose_move(piece, yard_movement)
            if forward is not None:
                actions.append(
                    LegalMoveAction(
                        action_id=f"{piece.id}:forward:{movement_value}",
                        piece_id=piece.id,
                        kind=MoveActionKind.FORWARD,
                        movement_value=forward.dice_value,
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
            action_id=f"{piece.id}:backward_capture:{movement_value}",
            piece_id=piece.id,
            kind=MoveActionKind.BACKWARD_CAPTURE,
            movement_value=movement_value,
            proposal=proposal,
        )

    @staticmethod
    def _all_pieces_in_yard(player: Player) -> bool:
        return all(piece.state is PieceState.IN_YARD for piece in player.pieces)

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
        if (
            action.kind is MoveActionKind.FORWARD
            and proposal.destination.global_outer_index in self.boost_positions
        ):
            return self._resolve_boost_displacement(proposal)
        if (
            action.kind is MoveActionKind.FORWARD
            and proposal.destination.global_outer_index in self.shield_square_positions
        ):
            proposal = replace(proposal, piece=replace(proposal.piece, has_shield=True))
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

    def _resolve_boost_displacement(self, proposal) -> CollisionOutcome:
        boost_index = proposal.destination.global_outer_index
        if boost_index is None:
            return self.collision_resolver.resolve(proposal, None)
        boosted_index = forward_global_index(boost_index)
        boosted_progress = backward_relative_progress(proposal.piece.owner_color, boosted_index)
        boosted_piece = replace(proposal.piece, path_progress=boosted_progress)
        boosted_proposal = replace(
            proposal,
            piece=boosted_piece,
            destination=proposal.destination.__class__.outer(
                proposal.piece.owner_color,
                boosted_progress,
                boosted_index,
            ),
        )
        return self.collision_resolver.resolve(
            boosted_proposal, self.outer_occupancies.get(boosted_index)
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
