"""Testable Pygame screen-flow state independent from rendering."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum

from ludo.app import GameFacade, GameSnapshot
from ludo.domain.players import MAX_PLAYER_NAME_LENGTH

MIN_PLAYER_COUNT = 2
MAX_PLAYER_COUNT = 4


class ScreenState(StrEnum):
    """Top-level application screens."""

    MAIN_MENU = "main_menu"
    PLAYER_SETUP = "player_setup"
    GAME = "game"
    RESULTS = "results"


@dataclass(slots=True)
class SetupForm:
    """Mutable player setup form state."""

    player_count: int = MIN_PLAYER_COUNT
    names: tuple[str, ...] = ("", "")

    def set_player_count(self, player_count: int) -> None:
        """Select the active player count and resize name fields."""
        if not MIN_PLAYER_COUNT <= player_count <= MAX_PLAYER_COUNT:
            msg = "Player count must be 2, 3, or 4."
            raise ValueError(msg)
        current_names = self.names[:player_count]
        missing = ("",) * (player_count - len(current_names))
        self.player_count = player_count
        self.names = (*current_names, *missing)

    def update_name(self, index: int, value: str) -> None:
        """Update one setup name, enforcing the approved 10-character limit."""
        if not 0 <= index < self.player_count:
            msg = f"Name field index {index} is out of range."
            raise IndexError(msg)
        names = list(self.names)
        names[index] = value[:MAX_PLAYER_NAME_LENGTH]
        self.names = tuple(names)

    @property
    def can_start(self) -> bool:
        """Return whether the form has all required non-blank names."""
        return len(self.names) == self.player_count and all(name.strip() for name in self.names)


@dataclass(slots=True)
class ScreenController:
    """Navigation and facade orchestration for the Pygame shell."""

    facade_factory: Callable[[], GameFacade] = GameFacade
    screen: ScreenState = ScreenState.MAIN_MENU
    setup: SetupForm = field(default_factory=SetupForm)
    facade: GameFacade | None = None
    paused: bool = False
    running: bool = True
    error_message: str | None = None

    def open_setup(self) -> None:
        """Move from the menu into player setup."""
        self.screen = ScreenState.PLAYER_SETUP
        self.paused = False
        self.error_message = None

    def back_to_menu(self) -> None:
        """Return to the main menu and clear active gameplay state."""
        self.screen = ScreenState.MAIN_MENU
        self.facade = None
        self.paused = False
        self.error_message = None

    def set_player_count(self, player_count: int) -> None:
        """Update setup player count."""
        self.setup.set_player_count(player_count)
        self.error_message = None

    def update_name(self, index: int, value: str) -> None:
        """Update one setup name field."""
        self.setup.update_name(index, value)
        self.error_message = None

    def start_game(self) -> GameSnapshot:
        """Create a match through the facade and enter the game screen."""
        if not self.setup.can_start:
            self.error_message = "Enter a name for every player."
            msg = "Player setup contains blank names."
            raise ValueError(msg)
        self.facade = self.facade_factory()
        snapshot = self.facade.start_match(self.setup.names).snapshot
        self.screen = ScreenState.GAME
        self.paused = False
        self.error_message = None
        return snapshot

    def show_results(self) -> None:
        """Navigate to placeholder final results."""
        self.screen = ScreenState.RESULTS
        self.paused = False
        self.error_message = None

    def play_again(self) -> None:
        """Return from results to setup for a new match."""
        self.facade = None
        self.screen = ScreenState.PLAYER_SETUP
        self.paused = False
        self.error_message = None

    def toggle_pause(self) -> None:
        """Toggle the game pause overlay."""
        if self.screen is ScreenState.GAME:
            self.paused = not self.paused

    def resume(self) -> None:
        """Resume gameplay from the pause overlay."""
        if self.screen is ScreenState.GAME:
            self.paused = False

    def quit(self) -> None:
        """Signal application shutdown."""
        self.running = False

    def snapshot(self) -> GameSnapshot | None:
        """Return current facade state when a match exists."""
        if self.facade is None:
            return None
        return self.facade.snapshot()
