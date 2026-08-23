"""Application-facing facade for UI and controller integrations."""

from __future__ import annotations

import time
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from ludo.domain.board import OUTER_PATH_LENGTH, BoardTopology
from ludo.domain.colors import PlayerColor
from ludo.domain.hazards import (
    HAZARD_PENALTY_STEPS,
    HazardRandomizer,
    clamped_backward_relative_progress,
    forward_global_index,
)
from ludo.domain.match import ColorRandomizer, Match
from ludo.domain.movement import MoveDestination, MoveDestinationKind
from ludo.domain.pieces import Piece, PieceState
from ludo.domain.players import Player
from ludo.domain.turns import (
    DECISION_TIMEOUT_SECONDS,
    Clock,
    Dice,
    MoveActionKind,
    SpecialDie,
    TurnEvent,
    TurnEventKind,
    TurnPhase,
)


class GameFacadeError(ValueError):
    """Raised when a public game command is invalid for the current facade state."""


class FacadeResultKind(StrEnum):
    """Public event categories emitted by facade commands."""

    MATCH_STARTED = "match_started"
    DICE_ROLLED = "dice_rolled"
    BASE_DICE_ROLLED = "base_dice_rolled"
    SPECIAL_DICE_ROLLED = "special_dice_rolled"
    NO_LEGAL_MOVE = "no_legal_move"
    PIECE_MOVED = "piece_moved"
    TRIPLE_SIX_CANCELLED = "triple_six_cancelled"
    TURN_PASSED = "turn_passed"
    ROLL_TIMEOUT = "roll_timeout"
    MOVE_TIMEOUT = "move_timeout"
    NO_TIMEOUT = "no_timeout"


@dataclass(frozen=True, slots=True)
class PieceSnapshot:
    """Read-only public view of a piece."""

    id: str
    owner_color: PlayerColor
    state: PieceState
    path_progress: int | None
    has_shield: bool = False


@dataclass(frozen=True, slots=True)
class PlayerSnapshot:
    """Read-only public view of a match player."""

    id: str
    name: str
    color: PlayerColor
    pieces: tuple[PieceSnapshot, ...]
    rank: int | None = None


@dataclass(frozen=True, slots=True)
class RankingSnapshot:
    """Read-only public standings entry."""

    rank: int
    player_id: str
    player_name: str
    color: PlayerColor


@dataclass(frozen=True, slots=True)
class MoveDestinationSnapshot:
    """Read-only destination for a legal move preview."""

    kind: MoveDestinationKind
    global_outer_index: int | None = None
    home_color: PlayerColor | None = None
    home_index: int | None = None


@dataclass(frozen=True, slots=True)
class MoveRouteStepSnapshot:
    """Read-only visual route step for an already legal move."""

    kind: MoveDestinationKind
    global_outer_index: int | None = None
    home_color: PlayerColor | None = None
    home_index: int | None = None


@dataclass(frozen=True, slots=True)
class LegalMoveSnapshot:
    """Read-only public view of a currently selectable piece."""

    piece_id: str
    owner_color: PlayerColor
    state: PieceState
    path_progress: int | None
    dice_value: int
    destination: MoveDestinationSnapshot
    route: tuple[MoveRouteStepSnapshot, ...]
    action_id: str = ""
    action_kind: MoveActionKind = MoveActionKind.FORWARD
    movement_value: int = 0


@dataclass(frozen=True, slots=True)
class OuterOccupancySnapshot:
    """Read-only public view of one occupied outer-path square."""

    global_index: int
    pieces: tuple[PieceSnapshot, ...]
    is_safe: bool
    is_protected: bool


@dataclass(frozen=True, slots=True)
class GameSnapshot:
    """Read-only public match state for UI and future controllers."""

    players: tuple[PlayerSnapshot, ...]
    inactive_colors: frozenset[PlayerColor]
    current_player: PlayerSnapshot | None
    phase: TurnPhase | None
    seconds_remaining: int
    decision_timeout_seconds: int
    current_dice_value: int | None
    legal_moves: tuple[LegalMoveSnapshot, ...]
    outer_occupancies: tuple[OuterOccupancySnapshot, ...]
    rankings: tuple[RankingSnapshot, ...]
    is_complete: bool
    current_special_bonus: int = 0
    special_bonus_applied: bool = False
    approved_movement_value: int | None = None
    hazard_positions: frozenset[int] = frozenset()
    boost_positions: frozenset[int] = frozenset()
    shield_square_positions: frozenset[int] = frozenset()


@dataclass(frozen=True, slots=True)
class FacadeResult:
    """Structured result of one public facade command."""

    kind: FacadeResultKind
    snapshot: GameSnapshot
    dice_value: int | None = None
    special_bonus: int = 0
    approved_movement_value: int | None = None
    special_bonus_applied: bool = False
    legal_moves: tuple[LegalMoveSnapshot, ...] = ()
    moved_piece: PieceSnapshot | None = None
    captured_piece: PieceSnapshot | None = None
    bonus_available: bool = False
    bonus_reasons: frozenset[str] = frozenset()
    turn_changed: bool = False
    ranked_players: tuple[RankingSnapshot, ...] = ()
    match_completed: bool = False
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
    def capture_occurred(self) -> bool:
        """Return whether the command captured an opponent piece."""
        return self.captured_piece is not None

    @property
    def piece_finished(self) -> bool:
        """Return whether the command moved a piece into Finished."""
        return self.moved_piece is not None and self.moved_piece.state is PieceState.FINISHED


@dataclass(slots=True)
class PausableClock:
    """Real monotonic clock that can freeze elapsed game time while paused."""

    _paused_at: float | None = None
    _paused_total: float = 0

    def now(self) -> float:
        """Return active, non-paused monotonic time."""
        current = self._paused_at if self._paused_at is not None else time.monotonic()
        return current - self._paused_total

    @property
    def paused(self) -> bool:
        """Return whether the clock is currently paused."""
        return self._paused_at is not None

    def pause(self) -> None:
        """Freeze active time."""
        if self._paused_at is None:
            self._paused_at = time.monotonic()

    def resume(self) -> None:
        """Resume active time without counting paused duration."""
        if self._paused_at is None:
            return
        self._paused_total += time.monotonic() - self._paused_at
        self._paused_at = None


@dataclass(slots=True)
class GameFacade:
    """Small public boundary over match, turn, movement, capture, and ranking services."""

    _match: Match | None = None
    _pausable_clock: PausableClock | None = None

    def start_match(
        self,
        player_names: Sequence[str],
        *,
        color_randomizer: ColorRandomizer | None = None,
        hazard_randomizer: HazardRandomizer | None = None,
        hazard_positions: frozenset[int] | None = None,
        boost_positions: frozenset[int] | None = None,
        shield_square_positions: frozenset[int] | None = None,
        dice: Dice | None = None,
        special_die: SpecialDie | None = None,
        clock: Clock | None = None,
    ) -> FacadeResult:
        """Create a new match and return its first public snapshot."""
        self._pausable_clock = PausableClock() if clock is None else None
        self._match = Match.create(
            tuple(player_names),
            color_randomizer=color_randomizer,
            hazard_randomizer=hazard_randomizer,
            hazard_positions=hazard_positions,
            boost_positions=boost_positions,
            shield_square_positions=shield_square_positions,
            dice=dice,
            special_die=special_die,
            clock=clock or self._pausable_clock,
        )
        snapshot = self.snapshot()
        return FacadeResult(FacadeResultKind.MATCH_STARTED, snapshot)

    @classmethod
    def from_match(cls, match: Match) -> GameFacade:
        """Wrap an existing match, useful for save/load and focused integration tests."""
        return cls(match)

    def pause(self) -> None:
        """Pause UI-created match time when supported."""
        if self._pausable_clock is not None:
            self._pausable_clock.pause()

    def resume(self) -> None:
        """Resume UI-created match time when supported."""
        if self._pausable_clock is not None:
            self._pausable_clock.resume()

    def snapshot(self) -> GameSnapshot:
        """Return an immutable public snapshot of the current match."""
        match = self._require_match()
        active_players = tuple(_player_snapshot(player) for player in match.turn_engine.players)
        rankings = _ranking_snapshots(match)
        ranked_players = tuple(
            _player_snapshot(entry.player, entry.rank) for entry in match.final_standings
        )
        current_player = self.current_player()
        return GameSnapshot(
            players=(*active_players, *ranked_players),
            inactive_colors=match.inactive_colors,
            current_player=current_player,
            phase=None if match.is_complete else match.turn_engine.phase,
            seconds_remaining=0 if match.is_complete else match.turn_engine.seconds_remaining,
            decision_timeout_seconds=0 if match.is_complete else DECISION_TIMEOUT_SECONDS,
            current_dice_value=None if match.is_complete else match.turn_engine.last_roll,
            current_special_bonus=0 if match.is_complete else match.turn_engine.last_special_bonus,
            special_bonus_applied=(
                False if match.is_complete else match.turn_engine.special_bonus_applied
            ),
            approved_movement_value=(
                None if match.is_complete else match.turn_engine.approved_movement_value
            ),
            legal_moves=self.legal_moves(),
            outer_occupancies=_outer_occupancy_snapshots(match),
            hazard_positions=match.turn_engine.hazard_positions,
            boost_positions=match.turn_engine.boost_positions,
            shield_square_positions=match.turn_engine.shield_square_positions,
            rankings=rankings,
            is_complete=match.is_complete,
        )

    def current_player(self) -> PlayerSnapshot | None:
        """Return the current eligible player, or ``None`` when the match is complete."""
        match = self._require_match()
        if match.is_complete or not match.turn_engine.players:
            return None
        return _player_snapshot(match.turn_engine.current_player)

    def current_phase(self) -> TurnPhase | None:
        """Return the public turn phase, or ``None`` after match completion."""
        match = self._require_match()
        return None if match.is_complete else match.turn_engine.phase

    def seconds_remaining(self) -> int:
        """Return remaining decision time for the active phase."""
        match = self._require_match()
        return 0 if match.is_complete else match.turn_engine.seconds_remaining

    def legal_moves(self) -> tuple[LegalMoveSnapshot, ...]:
        """Return currently selectable pieces for the active player."""
        match = self._require_match()
        if match.is_complete or match.turn_engine.phase is not TurnPhase.WAITING_FOR_MOVE:
            return ()
        if match.turn_engine.last_roll is None:
            return ()
        return tuple(
            _legal_move_snapshot(
                action,
                base_roll=match.turn_engine.last_roll,
                hazard_positions=match.turn_engine.hazard_positions,
                boost_positions=match.turn_engine.boost_positions,
            )
            for action in match.turn_engine.legal_actions
        )

    def rankings(self) -> tuple[RankingSnapshot, ...]:
        """Return standings in rank order."""
        return _ranking_snapshots(self._require_match())

    def is_complete(self) -> bool:
        """Return whether the match has assigned final standings."""
        return self._require_match().is_complete

    def player_state(self, player_id: str) -> PlayerSnapshot:
        """Return a public snapshot for an active or ranked player."""
        for player in self.snapshot().players:
            if player.id == player_id:
                return player
        msg = f"Unknown player {player_id}."
        raise GameFacadeError(msg)

    def piece_state(self, piece_id: str) -> PieceSnapshot:
        """Return a public snapshot for one piece."""
        for player in self.snapshot().players:
            for piece in player.pieces:
                if piece.id == piece_id:
                    return piece
        msg = f"Unknown piece {piece_id}."
        raise GameFacadeError(msg)

    def roll(self) -> FacadeResult:
        """Roll the normal die for the active player."""
        match = self._require_active_match()
        before_player_id = self._current_player_id(match)
        try:
            event = match.turn_engine.roll()
        except ValueError as exc:
            raise GameFacadeError(str(exc)) from exc
        return self._result_from_event(event, before_player_id)

    def roll_special(self) -> FacadeResult:
        """Roll the special die after the normal die has resolved."""
        match = self._require_active_match()
        before_player_id = self._current_player_id(match)
        try:
            event = match.turn_engine.roll_special()
        except ValueError as exc:
            raise GameFacadeError(str(exc)) from exc
        return self._result_from_event(event, before_player_id)

    def choose_piece(self, piece_id: str, action_id: str | None = None) -> FacadeResult:
        """Resolve a selected legal piece."""
        match = self._require_active_match()
        before_player_id = self._current_player_id(match)
        before_rank_count = len(match.rankings)
        try:
            event = match.turn_engine.select_piece(piece_id, action_id)
        except ValueError as exc:
            raise GameFacadeError(str(exc)) from exc
        match.evaluate_rankings()
        return self._result_from_event(event, before_player_id, before_rank_count)

    def complete_no_legal_move_notice(self) -> FacadeResult:
        """Finish no-legal feedback and pass the turn."""
        match = self._require_active_match()
        before_player_id = self._current_player_id(match)
        try:
            event = match.turn_engine.complete_no_legal_move_notice()
        except ValueError as exc:
            raise GameFacadeError(str(exc)) from exc
        return self._result_from_event(event, before_player_id)

    def expire_decision_if_needed(self) -> FacadeResult:
        """Expire the current roll or move decision if its timer has elapsed."""
        match = self._require_active_match()
        before_player_id = self._current_player_id(match)
        event = match.turn_engine.expire_decision_if_needed()
        if event is None:
            return FacadeResult(FacadeResultKind.NO_TIMEOUT, self.snapshot())
        return self._result_from_event(event, before_player_id)

    def _result_from_event(
        self,
        event: TurnEvent,
        before_player_id: str | None,
        before_rank_count: int | None = None,
    ) -> FacadeResult:
        match = self._require_match()
        ranked_players = ()
        if before_rank_count is not None:
            ranked_players = _ranking_snapshots(match)[before_rank_count:]
        snapshot = self.snapshot()
        moved_piece = _piece_snapshot(event.moved_piece) if event.moved_piece else None
        captured_piece = None
        if event.collision_outcome and event.collision_outcome.captured_piece:
            captured_piece = _piece_snapshot(event.collision_outcome.captured_piece)
        mover_ranked = any(entry.player.id == event.player.id for entry in match.rankings)
        return FacadeResult(
            kind=_result_kind(event.kind),
            snapshot=snapshot,
            dice_value=event.dice_value,
            special_bonus=event.special_bonus,
            approved_movement_value=event.approved_movement_value,
            special_bonus_applied=event.special_bonus_applied,
            legal_moves=snapshot.legal_moves,
            moved_piece=moved_piece,
            captured_piece=captured_piece,
            bonus_available=event.bonus_granted and not mover_ranked and not match.is_complete,
            bonus_reasons=event.bonus_reasons,
            turn_changed=before_player_id != self._current_player_id(match),
            ranked_players=ranked_players,
            match_completed=match.is_complete,
            action_kind=event.action_kind,
            hazard_triggered=event.hazard_triggered,
            hazard_from=event.hazard_from,
            hazard_to=event.hazard_to,
            boost_triggered=event.boost_triggered,
            boost_from=event.boost_from,
            boost_to=event.boost_to,
            shield_acquired=event.shield_acquired,
            shield_broken=event.shield_broken,
        )

    def _require_match(self) -> Match:
        if self._match is None:
            msg = "No match has been started."
            raise GameFacadeError(msg)
        return self._match

    def _require_active_match(self) -> Match:
        match = self._require_match()
        if match.is_complete:
            msg = "The match is complete."
            raise GameFacadeError(msg)
        return match

    @staticmethod
    def _current_player_id(match: Match) -> str | None:
        if match.is_complete or not match.turn_engine.players:
            return None
        return match.turn_engine.current_player.id


def _player_snapshot(player: Player, rank: int | None = None) -> PlayerSnapshot:
    return PlayerSnapshot(
        id=player.id,
        name=player.name,
        color=player.color,
        pieces=tuple(_piece_snapshot(piece) for piece in player.pieces),
        rank=rank,
    )


def _piece_snapshot(piece: Piece) -> PieceSnapshot:
    return PieceSnapshot(
        id=piece.id,
        owner_color=piece.owner_color,
        state=piece.state,
        path_progress=piece.path_progress,
        has_shield=piece.has_shield,
    )


def _outer_occupancy_snapshots(match: Match) -> tuple[OuterOccupancySnapshot, ...]:
    return tuple(
        OuterOccupancySnapshot(
            global_index=occupancy.global_index,
            pieces=tuple(_piece_snapshot(piece) for piece in occupancy.pieces),
            is_safe=match.turn_engine.collision_resolver.topology.is_safe_outer_position(
                occupancy.global_index
            ),
            is_protected=match.turn_engine.collision_resolver.is_protected_occupancy(occupancy),
        )
        for occupancy in sorted(
            match.turn_engine.outer_occupancies.values(), key=lambda item: item.global_index
        )
    )


def _legal_move_snapshot(
    action, *, base_roll: int, hazard_positions: frozenset[int], boost_positions: frozenset[int]
) -> LegalMoveSnapshot:
    piece = action.proposal.original_piece
    return LegalMoveSnapshot(
        action_id=action.action_id,
        piece_id=piece.id,
        owner_color=piece.owner_color,
        action_kind=action.kind,
        state=piece.state,
        path_progress=piece.path_progress,
        dice_value=base_roll,
        movement_value=action.movement_value,
        destination=_destination_snapshot(action.proposal.destination),
        route=_route_snapshot(
            piece,
            action.movement_value,
            action_kind=action.kind,
            hazard_positions=hazard_positions,
            boost_positions=boost_positions,
        ),
    )


def _route_snapshot(
    piece: Piece,
    dice_value: int,
    *,
    action_kind: MoveActionKind = MoveActionKind.FORWARD,
    hazard_positions: frozenset[int] = frozenset(),
    boost_positions: frozenset[int] = frozenset(),
) -> tuple[MoveRouteStepSnapshot, ...]:
    if action_kind is MoveActionKind.BACKWARD_CAPTURE:
        if piece.path_progress is None:
            msg = "Backward route requires path progress."
            raise ValueError(msg)
        return tuple(
            _outer_route_step(piece.owner_color, piece.path_progress - step)
            for step in range(1, dice_value + 1)
        )
    if piece.state is PieceState.IN_YARD:
        return (
            MoveRouteStepSnapshot(
                kind=MoveDestinationKind.OUTER_PATH,
                global_outer_index=BoardTopology().start_position(piece.owner_color),
            ),
        )
    if piece.state is PieceState.ON_OUTER_PATH:
        if piece.path_progress is None:
            msg = "Outer-path route requires path progress."
            raise ValueError(msg)
        route = tuple(
            _outer_route_step(piece.owner_color, piece.path_progress + step)
            for step in range(1, dice_value + 1)
        )
        final = route[-1] if route else None
        if (
            final is not None
            and final.global_outer_index is not None
            and final.global_outer_index in hazard_positions
        ):
            penalty_steps = tuple(
                _outer_route_step(
                    piece.owner_color,
                    clamped_backward_relative_progress(piece.path_progress + dice_value, step),
                )
                for step in range(
                    1,
                    min(HAZARD_PENALTY_STEPS, piece.path_progress + dice_value) + 1,
                )
            )
            return (*route, *penalty_steps)
        if (
            final is not None
            and final.global_outer_index is not None
            and final.global_outer_index in boost_positions
        ):
            first_boost = forward_global_index(final.global_outer_index, 1)
            second_boost = forward_global_index(final.global_outer_index, 2)
            return (
                *route,
                MoveRouteStepSnapshot(
                    MoveDestinationKind.OUTER_PATH, global_outer_index=first_boost
                ),
                MoveRouteStepSnapshot(
                    MoveDestinationKind.OUTER_PATH, global_outer_index=second_boost
                ),
            )
        return route
    if piece.state is PieceState.ON_HOME_PATH:
        if piece.path_progress is None:
            msg = "Home-Path route requires path progress."
            raise ValueError(msg)
        return tuple(
            _home_route_step(piece.owner_color, piece.path_progress + step)
            for step in range(1, dice_value + 1)
        )
    return ()


def _outer_route_step(color: PlayerColor, journey_progress: int) -> MoveRouteStepSnapshot:
    topology = BoardTopology()
    if journey_progress < 52:
        return MoveRouteStepSnapshot(
            kind=MoveDestinationKind.OUTER_PATH,
            global_outer_index=topology.global_outer_index(
                color, journey_progress % OUTER_PATH_LENGTH
            ),
        )
    if journey_progress < 57:
        return MoveRouteStepSnapshot(
            kind=MoveDestinationKind.HOME_PATH,
            home_color=color,
            home_index=journey_progress - 52,
        )
    return MoveRouteStepSnapshot(kind=MoveDestinationKind.FINISHED, home_color=color)


def _home_route_step(color: PlayerColor, home_progress: int) -> MoveRouteStepSnapshot:
    if home_progress < 5:
        return MoveRouteStepSnapshot(
            kind=MoveDestinationKind.HOME_PATH,
            home_color=color,
            home_index=home_progress,
        )
    return MoveRouteStepSnapshot(kind=MoveDestinationKind.FINISHED, home_color=color)


def _destination_snapshot(destination: MoveDestination) -> MoveDestinationSnapshot:
    if destination.kind is MoveDestinationKind.HOME_PATH:
        if destination.home_path_position is None:
            msg = "Home-Path destination requires a home path position."
            raise ValueError(msg)
        return MoveDestinationSnapshot(
            kind=destination.kind,
            home_color=destination.home_path_position.color,
            home_index=destination.home_path_position.index,
        )
    if destination.kind is MoveDestinationKind.FINISHED:
        return MoveDestinationSnapshot(
            kind=destination.kind,
            home_color=destination.color,
        )
    return MoveDestinationSnapshot(
        kind=destination.kind,
        global_outer_index=destination.global_outer_index,
    )


def _ranking_snapshots(match: Match) -> tuple[RankingSnapshot, ...]:
    return tuple(
        RankingSnapshot(
            rank=entry.rank,
            player_id=entry.player.id,
            player_name=entry.player.name,
            color=entry.player.color,
        )
        for entry in match.final_standings
    )


def _result_kind(event_kind: TurnEventKind) -> FacadeResultKind:
    return {
        TurnEventKind.ROLL_ACCEPTED: FacadeResultKind.DICE_ROLLED,
        TurnEventKind.BASE_ROLL_ACCEPTED: FacadeResultKind.BASE_DICE_ROLLED,
        TurnEventKind.SPECIAL_ROLL_ACCEPTED: FacadeResultKind.SPECIAL_DICE_ROLLED,
        TurnEventKind.NO_LEGAL_MOVE: FacadeResultKind.NO_LEGAL_MOVE,
        TurnEventKind.MOVE_RESOLVED: FacadeResultKind.PIECE_MOVED,
        TurnEventKind.TRIPLE_SIX_CANCELLED: FacadeResultKind.TRIPLE_SIX_CANCELLED,
        TurnEventKind.TURN_PASSED: FacadeResultKind.TURN_PASSED,
        TurnEventKind.ROLL_TIMEOUT: FacadeResultKind.ROLL_TIMEOUT,
        TurnEventKind.MOVE_TIMEOUT: FacadeResultKind.MOVE_TIMEOUT,
    }[event_kind]
