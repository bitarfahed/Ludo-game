"""Basic movement and legal-move calculation for Ludo pieces."""

from dataclasses import dataclass, field, replace
from enum import StrEnum

from ludo.domain.board import BoardTopology, FinishedDestination, HomePathPosition
from ludo.domain.colors import PlayerColor
from ludo.domain.pieces import Piece, PieceState
from ludo.domain.players import Player

MIN_DICE_VALUE = 1
MAX_DICE_VALUE = 6
MAX_MOVEMENT_VALUE = 8
OUTER_COMPLETION_PROGRESS = 52
FINISHED_JOURNEY_PROGRESS = 57


class DiceValueError(ValueError):
    """Raised when movement logic receives a dice value outside 1..6."""


class MoveDestinationKind(StrEnum):
    """Logical destination categories produced by basic movement."""

    OUTER_PATH = "outer_path"
    HOME_PATH = "home_path"
    FINISHED = "finished"


@dataclass(frozen=True, slots=True)
class MoveDestination:
    """A logical movement destination without screen or occupancy information."""

    kind: MoveDestinationKind
    color: PlayerColor
    relative_progress: int | None = None
    global_outer_index: int | None = None
    home_path_position: HomePathPosition | None = None
    finished_destination: FinishedDestination | None = None

    @classmethod
    def outer(
        cls, color: PlayerColor, relative_progress: int, global_outer_index: int
    ) -> "MoveDestination":
        """Create an outer-path destination."""
        return cls(
            kind=MoveDestinationKind.OUTER_PATH,
            color=color,
            relative_progress=relative_progress,
            global_outer_index=global_outer_index,
        )

    @classmethod
    def home(cls, home_path_position: HomePathPosition) -> "MoveDestination":
        """Create a private Home-Path destination."""
        return cls(
            kind=MoveDestinationKind.HOME_PATH,
            color=home_path_position.color,
            home_path_position=home_path_position,
            relative_progress=home_path_position.index,
        )

    @classmethod
    def finished(cls, color: PlayerColor) -> "MoveDestination":
        """Create a Finished destination."""
        return cls(
            kind=MoveDestinationKind.FINISHED,
            color=color,
            finished_destination=FinishedDestination(color),
        )


@dataclass(frozen=True, slots=True)
class ProposedMove:
    """The result of applying one dice value to one piece."""

    original_piece: Piece
    piece: Piece
    dice_value: int
    destination: MoveDestination


@dataclass(frozen=True, slots=True)
class MovementRules:
    """Calculate basic path movement without occupancy, capture, or turn rules."""

    topology: BoardTopology = field(default_factory=BoardTopology)

    def can_move(self, piece: Piece, dice_value: int) -> bool:
        """Return whether a piece has a basic legal move for a dice value."""
        return self.propose_move(piece, dice_value) is not None

    def propose_move(self, piece: Piece, dice_value: int) -> ProposedMove | None:
        """Calculate a legal movement proposal, or ``None`` when the roll cannot move the piece."""
        _validate_movement_value(dice_value)

        match piece.state:
            case PieceState.IN_YARD:
                return self._propose_yard_exit(piece, dice_value)
            case PieceState.ON_OUTER_PATH:
                return self._propose_outer_move(piece, dice_value)
            case PieceState.ON_HOME_PATH:
                return self._propose_home_move(piece, dice_value)
            case PieceState.FINISHED:
                return None

    def resolve_move(self, piece: Piece, dice_value: int) -> Piece:
        """Return the moved piece for a legal basic move."""
        proposal = self.propose_move(piece, dice_value)
        if proposal is None:
            msg = "Piece does not have a legal move for this dice value."
            raise ValueError(msg)
        return proposal.piece

    def legal_pieces(self, player: Player, dice_value: int) -> tuple[Piece, ...]:
        """Return the player's pieces that can legally use a dice value."""
        _validate_movement_value(dice_value)
        return tuple(piece for piece in player.pieces if self.can_move(piece, dice_value))

    def propose_backward_outer_capture(
        self, piece: Piece, movement_value: int
    ) -> ProposedMove | None:
        """Calculate the backward outer-path destination for capture-only checks."""
        _validate_movement_value(movement_value)
        if piece.state is not PieceState.ON_OUTER_PATH:
            return None
        if piece.path_progress is None:
            msg = "Outer-path pieces require path progress."
            raise ValueError(msg)
        if movement_value > piece.path_progress:
            return None
        relative_progress = piece.path_progress - movement_value
        return self._outer_result(piece, movement_value, relative_progress)

    def _propose_yard_exit(self, piece: Piece, dice_value: int) -> ProposedMove | None:
        if dice_value != MAX_DICE_VALUE:
            return None
        moved_piece = replace(
            piece, state=PieceState.ON_OUTER_PATH, path_progress=0, has_shield=False
        )
        destination = MoveDestination.outer(
            piece.owner_color,
            relative_progress=0,
            global_outer_index=self.topology.start_position(piece.owner_color),
        )
        return ProposedMove(piece, moved_piece, dice_value, destination)

    def _propose_outer_move(self, piece: Piece, dice_value: int) -> ProposedMove | None:
        if piece.path_progress is None:
            msg = "Outer-path pieces require path progress."
            raise ValueError(msg)

        journey_progress = piece.path_progress + dice_value
        if journey_progress < OUTER_COMPLETION_PROGRESS:
            return self._outer_result(piece, dice_value, journey_progress)
        if journey_progress < FINISHED_JOURNEY_PROGRESS:
            return self._home_result(
                piece, dice_value, home_index=journey_progress - OUTER_COMPLETION_PROGRESS
            )
        if journey_progress == FINISHED_JOURNEY_PROGRESS:
            return self._finished_result(piece, dice_value)
        return None

    def _propose_home_move(self, piece: Piece, dice_value: int) -> ProposedMove | None:
        if piece.path_progress is None:
            msg = "Home-Path pieces require path progress."
            raise ValueError(msg)

        home_progress = piece.path_progress + dice_value
        if home_progress < 5:
            return self._home_result(piece, dice_value, home_index=home_progress)
        if home_progress == 5:
            return self._finished_result(piece, dice_value)
        return None

    def _outer_result(self, piece: Piece, dice_value: int, relative_progress: int) -> ProposedMove:
        moved_piece = replace(
            piece, state=PieceState.ON_OUTER_PATH, path_progress=relative_progress
        )
        destination = MoveDestination.outer(
            piece.owner_color,
            relative_progress=relative_progress,
            global_outer_index=self.topology.global_outer_index(
                piece.owner_color, relative_progress
            ),
        )
        return ProposedMove(piece, moved_piece, dice_value, destination)

    def _home_result(self, piece: Piece, dice_value: int, home_index: int) -> ProposedMove:
        moved_piece = replace(
            piece,
            state=PieceState.ON_HOME_PATH,
            path_progress=home_index,
            has_shield=False,
        )
        destination = MoveDestination.home(HomePathPosition(piece.owner_color, home_index))
        return ProposedMove(piece, moved_piece, dice_value, destination)

    def _finished_result(self, piece: Piece, dice_value: int) -> ProposedMove:
        moved_piece = replace(
            piece, state=PieceState.FINISHED, path_progress=None, has_shield=False
        )
        destination = MoveDestination.finished(piece.owner_color)
        return ProposedMove(piece, moved_piece, dice_value, destination)


def _validate_dice_value(dice_value: int) -> None:
    if not MIN_DICE_VALUE <= dice_value <= MAX_DICE_VALUE:
        msg = f"dice value must be between {MIN_DICE_VALUE} and {MAX_DICE_VALUE}."
        raise DiceValueError(msg)


def _validate_movement_value(movement_value: int) -> None:
    if not MIN_DICE_VALUE <= movement_value <= MAX_MOVEMENT_VALUE:
        msg = f"movement value must be between {MIN_DICE_VALUE} and {MAX_MOVEMENT_VALUE}."
        raise DiceValueError(msg)
