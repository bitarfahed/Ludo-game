"""Core piece model for the Ludo domain."""

from dataclasses import dataclass
from enum import StrEnum

from ludo.domain.colors import PlayerColor


class PieceState(StrEnum):
    """Approved high-level states for a Ludo piece."""

    IN_YARD = "in_yard"
    ON_OUTER_PATH = "on_outer_path"
    ON_HOME_PATH = "on_home_path"
    FINISHED = "finished"


@dataclass(frozen=True, slots=True)
class Piece:
    """A stable player-owned piece without movement or rendering behavior.

    ``path_progress`` is intentionally generic at this stage. Future movement code can interpret it
    as logical route progress, while Yard and Finished pieces remain off the traversable path.
    """

    id: str
    owner_color: PlayerColor
    state: PieceState = PieceState.IN_YARD
    path_progress: int | None = None

    def __post_init__(self) -> None:
        """Validate identity, ownership, and state/location consistency."""
        if not self.id.strip():
            msg = "Piece identifier must be a non-empty string."
            raise ValueError(msg)
        if not isinstance(self.owner_color, PlayerColor):
            msg = "Piece owner_color must be a PlayerColor."
            raise TypeError(msg)
        if not isinstance(self.state, PieceState):
            msg = "Piece state must be a PieceState."
            raise TypeError(msg)

        if self.state in {PieceState.IN_YARD, PieceState.FINISHED}:
            self._validate_off_path()
            return

        self._validate_on_path()

    def _validate_off_path(self) -> None:
        if self.path_progress is not None:
            msg = f"{self.state.name} pieces cannot have path progress."
            raise ValueError(msg)

    def _validate_on_path(self) -> None:
        if self.path_progress is None:
            msg = f"{self.state.name} pieces require path progress."
            raise ValueError(msg)
        if self.path_progress < 0:
            msg = "Piece path progress must be non-negative."
            raise ValueError(msg)
