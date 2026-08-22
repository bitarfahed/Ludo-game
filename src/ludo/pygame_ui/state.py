"""Testable Pygame screen-flow state independent from rendering."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum

from ludo.app import GameFacade, GameSnapshot
from ludo.config import DEFAULT_ANIMATION_SETTINGS
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
    no_legal_notice_ms_remaining: int = 0
    feedback_message: str | None = None
    feedback_ms_remaining: int = 0

    @property
    def gameplay_input_blocked(self) -> bool:
        """Return whether UX feedback is currently blocking gameplay input."""
        return self.no_legal_notice_ms_remaining > 0

    def open_setup(self) -> None:
        """Move from the menu into player setup."""
        self.screen = ScreenState.PLAYER_SETUP
        self.paused = False
        self.error_message = None
        self._clear_feedback()

    def back_to_menu(self) -> None:
        """Return to the main menu and clear active gameplay state."""
        self.screen = ScreenState.MAIN_MENU
        self.facade = None
        self.paused = False
        self.error_message = None
        self._clear_feedback()

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
        self._clear_feedback()
        return snapshot

    def show_results(self) -> None:
        """Navigate to placeholder final results."""
        self.screen = ScreenState.RESULTS
        self.paused = False
        self.error_message = None
        self._clear_feedback()

    def restart_match(self) -> GameSnapshot:
        """Start a fresh match from the current setup values."""
        return self.start_game()

    def play_again(self) -> GameSnapshot:
        """Start a fresh match from the previous setup."""
        return self.start_game()

    def toggle_pause(self) -> None:
        """Toggle the game pause overlay."""
        if self.screen is ScreenState.GAME:
            self.paused = not self.paused
            if self.facade is not None:
                if self.paused:
                    self.facade.pause()
                else:
                    self.facade.resume()

    def resume(self) -> None:
        """Resume gameplay from the pause overlay."""
        if self.screen is ScreenState.GAME:
            self.paused = False
            if self.facade is not None:
                self.facade.resume()

    def quit(self) -> None:
        """Signal application shutdown."""
        self.running = False

    def snapshot(self) -> GameSnapshot | None:
        """Return current facade state when a match exists."""
        if self.facade is None:
            return None
        return self.facade.snapshot()

    def start_no_legal_notice(self) -> None:
        """Start the approved no-legal-move countdown UX."""
        self.no_legal_notice_ms_remaining = DEFAULT_ANIMATION_SETTINGS.no_legal_notice_ms
        self.feedback_message = "NO LEGAL MOVE"
        self.feedback_ms_remaining = self.no_legal_notice_ms_remaining

    def show_feedback(self, message: str) -> None:
        """Show short non-blocking gameplay feedback."""
        self.feedback_message = message
        self.feedback_ms_remaining = DEFAULT_ANIMATION_SETTINGS.feedback_notice_ms

    def update_feedback(self, delta_ms: int) -> None:
        """Advance transient UX countdowns."""
        if self.feedback_ms_remaining > 0:
            self.feedback_ms_remaining = max(0, self.feedback_ms_remaining - delta_ms)
            if self.feedback_ms_remaining == 0:
                self.feedback_message = None
        if self.no_legal_notice_ms_remaining > 0:
            self.no_legal_notice_ms_remaining = max(
                0, self.no_legal_notice_ms_remaining - delta_ms
            )

    def _clear_feedback(self) -> None:
        self.no_legal_notice_ms_remaining = 0
        self.feedback_message = None
        self.feedback_ms_remaining = 0
