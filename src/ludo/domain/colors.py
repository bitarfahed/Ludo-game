"""Domain color identifiers for active Ludo players."""

from enum import StrEnum


class PlayerColor(StrEnum):
    """Traditional Ludo player colors used by the domain model."""

    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"

    @property
    def piece_symbol(self) -> str:
        """Return the approved compact symbol for this color."""
        return {
            PlayerColor.RED: "r",
            PlayerColor.GREEN: "g",
            PlayerColor.YELLOW: "y",
            PlayerColor.BLUE: "b",
        }[self]
