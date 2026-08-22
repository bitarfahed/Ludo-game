"""Pygame screen rendering and input dispatch for the shell milestone."""

from __future__ import annotations

from contextlib import suppress

import pygame

from ludo.app import FacadeResult, FacadeResultKind, GameFacadeError
from ludo.audio import AudioEvent, AudioService
from ludo.domain.turns import TurnPhase
from ludo.pygame_ui import layout, theme
from ludo.pygame_ui.animation import AnimationManager
from ludo.pygame_ui.board_renderer import BoardRenderer
from ludo.pygame_ui.controls import Button, draw_text
from ludo.pygame_ui.gameplay_renderer import GameplayRenderer
from ludo.pygame_ui.interaction import GameplayInteractionController
from ludo.pygame_ui.state import ScreenController, ScreenState


class ScreenRenderer:
    """Render and dispatch high-level UI events for all shell screens."""

    def __init__(self) -> None:
        self.title_font = pygame.font.Font(None, 56)
        self.font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 24)
        self.board_renderer = BoardRenderer()
        self.gameplay_renderer = GameplayRenderer(self.board_renderer.geometry)
        self.animation = AnimationManager()
        self.audio = AudioService()
        self.interaction = GameplayInteractionController(
            self.board_renderer.geometry,
            animation=self.animation,
            audio=self.audio,
        )
        self.active_name_index: int | None = None

    def update(self, delta_ms: int, controller: ScreenController) -> None:
        """Advance presentation systems."""
        self.animation.update(delta_ms, paused=controller.paused)
        if controller.paused:
            return
        controller.update_feedback(delta_ms)
        if controller.screen is not ScreenState.GAME or controller.facade is None:
            return
        if controller.no_legal_notice_ms_remaining == 0:
            self._complete_no_legal_if_ready(controller)
            self._expire_decision_if_ready(controller)
        snapshot = controller.snapshot()
        if snapshot is not None and snapshot.is_complete and not self.animation.input_locked:
            controller.show_results()

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
        if event.type == pygame.MOUSEMOTION:
            self.interaction.handle_hover(event.pos, controller)
            return
        if event.type == pygame.KEYDOWN and controller.screen is ScreenState.PLAYER_SETUP:
            self._handle_setup_key(event, controller)

    def _handle_click(self, position: tuple[int, int], controller: ScreenController) -> None:
        if controller.paused:
            self._apply_command(_command_at(position, layout.pause_buttons()), controller)
            return
        if controller.screen is ScreenState.GAME and self.interaction.handle_click(
            position, controller
        ):
            self._process_result(self.interaction.pop_result(), controller)
            return
        buttons = layout.buttons_for(controller)
        command = _command_at(position, buttons)
        if command is not None:
            self.audio.play(AudioEvent.UI_CLICK)
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
            self._reset_presentation()
            controller.open_setup()
        elif command == "quit":
            controller.quit()
        elif command == "back":
            self._reset_presentation()
            controller.back_to_menu()
        elif command == "start_game":
            self._reset_presentation()
            _try_start_game(controller)
        elif command.startswith("count:"):
            controller.set_player_count(int(command.removeprefix("count:")))
        elif command == "resume":
            controller.resume()
        elif command == "restart_match":
            self._restart_match(controller)
        elif command == "main_menu":
            self._reset_presentation()
            controller.back_to_menu()
        elif command == "play_again":
            self._play_again(controller)

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
        self._draw_feedback(surface, controller)
        self.gameplay_renderer.draw(
            surface,
            snapshot,
            self.font,
            self.small_font,
            self.interaction.preview,
            self.interaction.inspection,
            self.animation,
        )

    def _draw_results(self, surface: pygame.Surface, controller: ScreenController) -> None:
        _draw_title(surface, self.title_font, "Final Results")
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

    def _process_result(
        self, result: FacadeResult | None, controller: ScreenController
    ) -> None:
        if result is None:
            return
        if result.kind is FacadeResultKind.NO_LEGAL_MOVE:
            controller.start_no_legal_notice()
            return
        if result.kind is FacadeResultKind.ROLL_TIMEOUT:
            controller.show_feedback("ROLL TIMEOUT")
        elif result.kind is FacadeResultKind.MOVE_TIMEOUT:
            controller.show_feedback("MOVE TIMEOUT")
        elif result.ranked_players:
            first_rank = result.ranked_players[0]
            controller.show_feedback(f"{first_rank.player_name} finished! Rank {first_rank.rank}")
        if result.match_completed and not self.animation.input_locked:
            controller.show_results()

    def _complete_no_legal_if_ready(self, controller: ScreenController) -> None:
        snapshot = controller.snapshot()
        if snapshot is None or snapshot.phase is not TurnPhase.NO_LEGAL_MOVE:
            return
        try:
            result = controller.facade.complete_no_legal_move_notice()
        except (AttributeError, GameFacadeError):
            return
        self._process_result(result, controller)

    def _expire_decision_if_ready(self, controller: ScreenController) -> None:
        if self.animation.input_locked or controller.facade is None:
            return
        try:
            result = controller.facade.expire_decision_if_needed()
        except GameFacadeError:
            return
        if result.kind is not FacadeResultKind.NO_TIMEOUT:
            self._process_result(result, controller)

    def _restart_match(self, controller: ScreenController) -> None:
        self._reset_presentation()
        with suppress(ValueError):
            controller.restart_match()

    def _play_again(self, controller: ScreenController) -> None:
        self._reset_presentation()
        with suppress(ValueError):
            controller.play_again()

    def _reset_presentation(self) -> None:
        self.animation = AnimationManager()
        self.interaction.animation = self.animation
        self.interaction.preview = None
        self.interaction.inspection = None
        self.interaction.latest_result = None

    def _draw_feedback(self, surface: pygame.Surface, controller: ScreenController) -> None:
        if controller.feedback_message is None:
            return
        suffix = ""
        if controller.no_legal_notice_ms_remaining > 0:
            seconds = max(1, (controller.no_legal_notice_ms_remaining + 999) // 1000)
            suffix = f" ({seconds})"
        label = self.font.render(f"{controller.feedback_message}{suffix}", True, theme.TEXT)
        rect = label.get_rect(center=(480, 95)).inflate(24, 12)
        pygame.draw.rect(surface, theme.SURFACE, rect, border_radius=6)
        pygame.draw.rect(surface, theme.BORDER, rect, width=2, border_radius=6)
        surface.blit(label, label.get_rect(center=rect.center))


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
