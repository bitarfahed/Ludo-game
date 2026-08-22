"""Static shell-screen layout helpers."""

from __future__ import annotations

import pygame

from ludo.pygame_ui.controls import Button, TextField
from ludo.pygame_ui.state import MAX_PLAYER_COUNT, MIN_PLAYER_COUNT, ScreenController, ScreenState


def main_menu_buttons() -> tuple[Button, ...]:
    """Return main-menu buttons."""
    return (
        Button("open_setup", "Start Game", pygame.Rect(380, 235, 200, 48)),
        Button("quit", "Quit", pygame.Rect(380, 300, 200, 48)),
    )


def count_buttons(active_count: int) -> tuple[Button, ...]:
    """Return player-count selector buttons."""
    buttons = []
    for offset, count in enumerate(range(MIN_PLAYER_COUNT, MAX_PLAYER_COUNT + 1)):
        label = f"{count} Players" if count == active_count else str(count)
        rect = pygame.Rect(300 + offset * 115, 175, 100, 42)
        buttons.append(Button(f"count:{count}", label, rect))
    return tuple(buttons)


def name_fields(controller: ScreenController) -> tuple[TextField, ...]:
    """Return setup-name fields for the current player count."""
    return tuple(
        TextField(index=index, rect=pygame.Rect(300, 245 + index * 54, 360, 42))
        for index in range(controller.setup.player_count)
    )


def name_field_at(position: tuple[int, int], controller: ScreenController) -> int | None:
    """Return the clicked setup-name field index."""
    if controller.screen is not ScreenState.PLAYER_SETUP:
        return None
    for field in name_fields(controller):
        if field.contains(position):
            return field.index
    return None


def setup_buttons(can_start: bool) -> tuple[Button, ...]:
    """Return setup action buttons."""
    return (
        Button("back", "Back", pygame.Rect(300, 520, 160, 46)),
        Button("start_game", "Start Game", pygame.Rect(500, 520, 160, 46), enabled=can_start),
    )


def results_buttons() -> tuple[Button, ...]:
    """Return results action buttons."""
    return (
        Button("play_again", "Play Again", pygame.Rect(275, 520, 130, 46)),
        Button("main_menu", "Main Menu", pygame.Rect(415, 520, 130, 46)),
        Button("quit", "Quit", pygame.Rect(555, 520, 130, 46)),
    )


def buttons_for(controller: ScreenController) -> tuple[Button, ...]:
    """Return clickable buttons for the active unpaused screen."""
    if controller.screen is ScreenState.MAIN_MENU:
        return main_menu_buttons()
    if controller.screen is ScreenState.PLAYER_SETUP:
        return (
            *count_buttons(controller.setup.player_count),
            *setup_buttons(controller.setup.can_start),
        )
    if controller.screen is ScreenState.RESULTS:
        return results_buttons()
    return ()


def pause_buttons() -> tuple[Button, ...]:
    """Return pause-overlay buttons."""
    return (
        Button("resume", "Resume", pygame.Rect(380, 210, 200, 42)),
        Button("restart_match", "Restart Match", pygame.Rect(380, 262, 200, 42)),
        Button("main_menu", "Main Menu", pygame.Rect(380, 314, 200, 42)),
        Button("quit", "Quit", pygame.Rect(380, 366, 200, 42)),
    )
