"""Pygame screen rendering and input dispatch for the shell milestone."""

from __future__ import annotations

from contextlib import suppress

import pygame

from ludo.pygame_ui import layout, theme
from ludo.pygame_ui.board_renderer import BoardRenderer
from ludo.pygame_ui.controls import Button, draw_text
from ludo.pygame_ui.state import ScreenController, ScreenState


class ScreenRenderer:
    """Render and dispatch high-level UI events for all shell screens."""

    def __init__(self) -> None:
        self.title_font = pygame.font.Font(None, 56)
        self.font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 24)
        self.board_renderer = BoardRenderer()
        self.active_name_index: int | None = None

    def draw(self, surface: pygame.Surface, controller: ScreenController) -> None:
        """Draw the active screen."""
        surface.fill(theme.BACKGROUND)
        if controller.screen is ScreenState.MAIN_MENU:
            self._draw_main_menu(surface)
        elif controller.screen is ScreenState.PLAYER_SETUP:
            self._draw_setup(surface, controller)
        elif controller.screen is ScreenState.GAME:
            self._draw_game(surface, controller)
        elif controller.screen is ScreenState.RESULTS:
            self._draw_results(surface, controller)
        if controller.paused:
            self._draw_pause_overlay(surface)

    def handle_event(self, event: pygame.event.Event, controller: ScreenController) -> None:
        """Apply one Pygame event to the screen controller."""
        if event.type == pygame.QUIT:
            controller.quit()
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            controller.toggle_pause()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos, controller)
            return
        if event.type == pygame.KEYDOWN and controller.screen is ScreenState.PLAYER_SETUP:
            self._handle_setup_key(event, controller)

    def _handle_click(self, position: tuple[int, int], controller: ScreenController) -> None:
        if controller.paused:
            self._apply_command(_command_at(position, layout.pause_buttons()), controller)
            return
        buttons = layout.buttons_for(controller)
        command = _command_at(position, buttons)
        if command is not None:
            self._apply_command(command, controller)
            return
        self.active_name_index = layout.name_field_at(position, controller)

    def _handle_setup_key(self, event: pygame.event.Event, controller: ScreenController) -> None:
        if self.active_name_index is None:
            return
        current = controller.setup.names[self.active_name_index]
        if event.key == pygame.K_BACKSPACE:
            controller.update_name(self.active_name_index, current[:-1])
        elif event.unicode and event.unicode.isprintable():
            controller.update_name(self.active_name_index, f"{current}{event.unicode}")

    def _apply_command(self, command: str | None, controller: ScreenController) -> None:
        if command is None:
            return
        if command == "open_setup":
            controller.open_setup()
        elif command == "quit":
            controller.quit()
        elif command == "back":
            controller.back_to_menu()
        elif command == "start_game":
            _try_start_game(controller)
        elif command.startswith("count:"):
            controller.set_player_count(int(command.removeprefix("count:")))
        elif command == "resume":
            controller.resume()
        elif command == "main_menu":
            controller.back_to_menu()
        elif command == "play_again":
            controller.play_again()

    def _draw_main_menu(self, surface: pygame.Surface) -> None:
        _draw_title(surface, self.title_font, "Ludo")
        for button in layout.main_menu_buttons():
            button.draw(surface, self.font)

    def _draw_setup(self, surface: pygame.Surface, controller: ScreenController) -> None:
        _draw_title(surface, self.title_font, "Player Setup")
        draw_text(surface, self.font, "Players", (300, 138))
        for button in layout.count_buttons(controller.setup.player_count):
            button.draw(surface, self.font)
        for field in layout.name_fields(controller):
            field.draw(
                surface,
                self.font,
                controller.setup.names[field.index],
                field.index == self.active_name_index,
            )
        if controller.error_message:
            draw_text(surface, self.small_font, controller.error_message, (300, 482), theme.DANGER)
        for button in layout.setup_buttons(controller.setup.can_start):
            button.draw(surface, self.font)

    def _draw_game(self, surface: pygame.Surface, controller: ScreenController) -> None:
        snapshot = controller.snapshot()
        if snapshot is None:
            draw_text(surface, self.font, "No match is active.", (300, 150))
            return
        self.board_renderer.draw(surface, snapshot, self.font, self.small_font)
        current = snapshot.current_player.name if snapshot.current_player else "None"
        draw_text(surface, self.small_font, f"Current: {current}", (28, 24), theme.TEXT)

    def _draw_results(self, surface: pygame.Surface, controller: ScreenController) -> None:
        _draw_title(surface, self.title_font, "Results")
        rankings = controller.facade.rankings() if controller.facade else ()
        if rankings:
            for index, entry in enumerate(rankings):
                draw_text(
                    surface,
                    self.font,
                    f"{entry.rank}. {entry.player_name}",
                    (340, 145 + index * 38),
                )
        else:
            draw_text(surface, self.font, "Final standings will appear here.", (300, 150))
        for button in layout.results_buttons():
            button.draw(surface, self.font)

    def _draw_pause_overlay(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill(theme.OVERLAY)
        surface.blit(overlay, (0, 0))
        draw_text(surface, self.title_font, "Paused", (395, 145), theme.SURFACE)
        for button in layout.pause_buttons():
            button.draw(surface, self.font)


def _try_start_game(controller: ScreenController) -> None:
    with suppress(ValueError):
        controller.start_game()


def _draw_title(surface: pygame.Surface, font: pygame.font.Font, title: str) -> None:
    label = font.render(title, True, theme.TEXT)
    surface.blit(label, label.get_rect(center=(480, 80)))


def _command_at(position: tuple[int, int], buttons: tuple[Button, ...]) -> str | None:
    for button in buttons:
        command = button.command_at(position)
        if command is not None:
            return command
    return None
