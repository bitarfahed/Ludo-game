"""Outer-path occupancy, capture, and protection-block resolution."""

from dataclasses import dataclass, field, replace

from ludo.domain.board import OUTER_PATH_LENGTH, BoardTopology
from ludo.domain.movement import MoveDestinationKind, ProposedMove
from ludo.domain.pieces import Piece, PieceState


@dataclass(frozen=True, slots=True)
class OuterPathOccupancy:
    """Pieces currently sharing one global outer-path square."""

    global_index: int
    pieces: tuple[Piece, ...]
    was_protected: bool = False

    def __post_init__(self) -> None:
        if not 0 <= self.global_index < OUTER_PATH_LENGTH:
            msg = f"global outer index must be between 0 and {OUTER_PATH_LENGTH - 1}."
            raise ValueError(msg)
        if any(piece.state is not PieceState.ON_OUTER_PATH for piece in self.pieces):
            msg = "Outer-path occupancy can contain only ON_OUTER_PATH pieces."
            raise ValueError(msg)
        if len({piece.id for piece in self.pieces}) != len(self.pieces):
            msg = "Outer-path occupancy cannot contain duplicate piece identifiers."
            raise ValueError(msg)
        if len(self.pieces) < 2 and self.was_protected:
            object.__setattr__(self, "was_protected", False)


@dataclass(frozen=True, slots=True)
class CollisionOutcome:
    """Inspectable result of applying destination occupancy rules to a proposed move."""

    moved_piece: Piece
    captured_piece: Piece | None
    destination_occupancy: OuterPathOccupancy | None
    destination_protected: bool
    shield_broken_piece: Piece | None = None

    @property
    def capture_occurred(self) -> bool:
        """Return whether an opponent piece was captured."""
        return self.captured_piece is not None


@dataclass(frozen=True, slots=True)
class CollisionResolver:
    """Resolve outer-square capture and protection without turn or bonus behavior."""

    topology: BoardTopology = field(default_factory=BoardTopology)

    def resolve(
        self, proposed_move: ProposedMove, occupancy: OuterPathOccupancy | None = None
    ) -> CollisionOutcome:
        """Resolve destination occupancy for a proposed move."""
        if proposed_move.destination.kind is not MoveDestinationKind.OUTER_PATH:
            return CollisionOutcome(
                moved_piece=proposed_move.piece,
                captured_piece=None,
                destination_occupancy=None,
                destination_protected=False,
            )

        destination_index = proposed_move.destination.global_outer_index
        if destination_index is None:
            msg = "Outer-path move destination requires a global outer index."
            raise ValueError(msg)

        if occupancy is None or occupancy.global_index != destination_index:
            destination_occupancy = OuterPathOccupancy(
                global_index=destination_index, pieces=(proposed_move.piece,)
            )
            return CollisionOutcome(proposed_move.piece, None, destination_occupancy, False)

        if self._is_safe(occupancy.global_index):
            return self._join_without_capture(proposed_move.piece, occupancy)

        if self.is_protected_occupancy(occupancy):
            return self._join_without_capture(proposed_move.piece, occupancy)

        vulnerable_piece = self._vulnerable_opponent(proposed_move.piece, occupancy)
        if vulnerable_piece is not None:
            if vulnerable_piece.has_shield:
                unshielded = replace(vulnerable_piece, has_shield=False)
                destination_occupancy = OuterPathOccupancy(
                    global_index=occupancy.global_index,
                    pieces=(unshielded, proposed_move.piece),
                    was_protected=False,
                )
                return CollisionOutcome(
                    proposed_move.piece,
                    None,
                    destination_occupancy,
                    self.is_protected_occupancy(destination_occupancy),
                    unshielded,
                )
            captured_piece = replace(
                vulnerable_piece,
                state=PieceState.IN_YARD,
                path_progress=None,
                has_shield=False,
            )
            destination_occupancy = OuterPathOccupancy(
                global_index=occupancy.global_index, pieces=(proposed_move.piece,)
            )
            return CollisionOutcome(
                proposed_move.piece, captured_piece, destination_occupancy, False
            )

        return self._join_without_capture(proposed_move.piece, occupancy)

    def is_protected_occupancy(self, occupancy: OuterPathOccupancy) -> bool:
        """Return whether the occupancy is protected from capture."""
        if self._is_safe(occupancy.global_index):
            return bool(occupancy.pieces)
        if len(occupancy.pieces) < 2:
            return False
        if occupancy.was_protected:
            return True
        return len({piece.owner_color for piece in occupancy.pieces}) == 1

    def _join_without_capture(
        self, moved_piece: Piece, occupancy: OuterPathOccupancy
    ) -> CollisionOutcome:
        pieces = (*occupancy.pieces, moved_piece)
        destination_occupancy = OuterPathOccupancy(
            global_index=occupancy.global_index,
            pieces=pieces,
            was_protected=self._should_persist_protection(occupancy, pieces),
        )
        return CollisionOutcome(
            moved_piece=moved_piece,
            captured_piece=None,
            destination_occupancy=destination_occupancy,
            destination_protected=self.is_protected_occupancy(destination_occupancy),
        )

    def _should_persist_protection(
        self, occupancy: OuterPathOccupancy, pieces: tuple[Piece, ...]
    ) -> bool:
        if self._is_safe(occupancy.global_index):
            return False
        if len(pieces) < 2:
            return False
        if occupancy.was_protected or self.is_protected_occupancy(occupancy):
            return True
        return len({piece.owner_color for piece in pieces}) == 1

    @staticmethod
    def _vulnerable_opponent(moved_piece: Piece, occupancy: OuterPathOccupancy) -> Piece | None:
        if len(occupancy.pieces) != 1:
            return None
        existing_piece = occupancy.pieces[0]
        if existing_piece.owner_color is moved_piece.owner_color:
            return None
        return existing_piece

    def _is_safe(self, global_index: int) -> bool:
        return self.topology.is_safe_outer_position(global_index)
