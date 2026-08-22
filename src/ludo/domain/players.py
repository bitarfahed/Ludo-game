"""Core player model for the Ludo domain."""

from dataclasses import dataclass, field

from ludo.domain.colors import PlayerColor
from ludo.domain.pieces import Piece

PIECES_PER_PLAYER = 4
MAX_PLAYER_NAME_LENGTH = 10


@dataclass(frozen=True, slots=True)
class Player:
    """A human participant assigned one active color and exactly four pieces."""

    id: str
    name: str
    color: PlayerColor
    pieces: tuple[Piece, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate identity, name, color, and piece ownership invariants."""
        if not self.id.strip():
            msg = "Player identifier must be a non-empty string."
            raise ValueError(msg)
        if not isinstance(self.color, PlayerColor):
            msg = "Player color must be a PlayerColor."
            raise TypeError(msg)

        normalized_name = self.name.strip()
        self._validate_name(normalized_name)
        object.__setattr__(self, "name", normalized_name)

        pieces = self.pieces or self._create_initial_pieces()
        self._validate_pieces(pieces)
        object.__setattr__(self, "pieces", tuple(pieces))

    def _create_initial_pieces(self) -> tuple[Piece, ...]:
        return tuple(
            Piece(id=f"{self.id}-piece-{piece_number}", owner_color=self.color)
            for piece_number in range(1, PIECES_PER_PLAYER + 1)
        )

    @staticmethod
    def _validate_name(name: str) -> None:
        if not name:
            msg = "Player name must be non-empty."
            raise ValueError(msg)
        if len(name) > MAX_PLAYER_NAME_LENGTH:
            msg = f"Player name must be at most {MAX_PLAYER_NAME_LENGTH} characters."
            raise ValueError(msg)

    def _validate_pieces(self, pieces: tuple[Piece, ...]) -> None:
        if len(pieces) != PIECES_PER_PLAYER:
            msg = f"Player must own exactly four pieces, got {len(pieces)}."
            raise ValueError(msg)

        piece_ids = [piece.id for piece in pieces]
        if len(set(piece_ids)) != PIECES_PER_PLAYER:
            msg = "Player piece identifiers must be unique."
            raise ValueError(msg)

        if any(piece.owner_color is not self.color for piece in pieces):
            msg = "All player pieces must belong to the player's assigned color."
            raise ValueError(msg)
