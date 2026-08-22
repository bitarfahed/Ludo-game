"""Smoke tests for Pygame shell rendering and event dispatch."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from ludo.pygame_ui.controls import Button
from ludo.pygame_ui.main import LudoApplication, main
from ludo.pygame_ui.screens import ScreenRenderer
from ludo.pygame_ui.state import ScreenController, ScreenState


@pytest.fixture
def pygame_context() -> pygame.Surface:
    pygame.init()
    surface = pygame.Surface((960, 640))
    yield surface
    pygame.quit()


def test_button_command_respects_enabled_state(pygame_context: pygame.Surface) -> None:
    font = pygame.font.Font(None, 24)
    button = Button("go", "Go", pygame.Rect(10, 10, 80, 30))
    disabled = Button("stop", "Stop", pygame.Rect(100, 10, 80, 30), enabled=False)

    button.draw(pygame_context, font)
    disabled.draw(pygame_context, font)

    assert button.command_at((15, 15)) == "go"
    assert disabled.command_at((105, 15)) is None


def test_renderer_draws_all_screens_and_pause_overlay(pygame_context: pygame.Surface) -> None:
    renderer = ScreenRenderer()
    controller = ScreenController()

    renderer.draw(pygame_context, controller)
    controller.open_setup()
    renderer.draw(pygame_context, controller)
    controller.update_name(0, "Alice")
    controller.update_name(1, "Bob")
    controller.start_game()
    renderer.draw(pygame_context, controller)
    controller.toggle_pause()
    renderer.draw(pygame_context, controller)
    controller.show_results()
    renderer.draw(pygame_context, controller)


@pytest.mark.usefixtures("pygame_context")
def test_renderer_clicks_main_menu_setup_and_back() -> None:
    renderer = ScreenRenderer()
    controller = ScreenController()

    renderer.handle_event(_click((390, 250)), controller)
    assert controller.screen is ScreenState.PLAYER_SETUP

    renderer.handle_event(_click((310, 535)), controller)
    assert controller.screen is ScreenState.MAIN_MENU


@pytest.mark.usefixtures("pygame_context")
def test_renderer_setup_count_fields_typing_and_start() -> None:
    renderer = ScreenRenderer()
    controller = ScreenController()
    controller.open_setup()

    renderer.handle_event(_click((530, 190)), controller)
    assert controller.setup.player_count == 4
    renderer.handle_event(_click((310, 250)), controller)
    renderer.handle_event(_key(pygame.K_a, "A"), controller)
    renderer.handle_event(_key(pygame.K_l, "l"), controller)
    renderer.handle_event(_key(pygame.K_BACKSPACE, ""), controller)
    assert controller.setup.names[0] == "A"
    for index, name in enumerate(("Alice", "Bob", "Cy", "Dee")):
        controller.update_name(index, name)

    renderer.handle_event(_click((520, 535)), controller)

    assert controller.screen is ScreenState.GAME
    assert controller.snapshot() is not None


@pytest.mark.usefixtures("pygame_context")
def test_renderer_setup_start_with_blank_name_stays_on_setup() -> None:
    renderer = ScreenRenderer()
    controller = ScreenController()
    controller.open_setup()
    controller.update_name(0, "Alice")

    renderer.handle_event(_click((520, 535)), controller)

    assert controller.screen is ScreenState.PLAYER_SETUP


@pytest.mark.usefixtures("pygame_context")
def test_escape_toggles_pause_and_pause_buttons_work() -> None:
    renderer = ScreenRenderer()
    controller = _started_controller()

    renderer.handle_event(_key(pygame.K_ESCAPE, ""), controller)
    assert controller.paused
    renderer.handle_event(_click((390, 245)), controller)
    assert not controller.paused

    renderer.handle_event(_key(pygame.K_ESCAPE, ""), controller)
    renderer.handle_event(_click((390, 307)), controller)
    assert controller.screen is ScreenState.MAIN_MENU


@pytest.mark.usefixtures("pygame_context")
def test_pause_quit_and_window_quit_signal_shutdown() -> None:
    renderer = ScreenRenderer()
    controller = _started_controller()
    controller.toggle_pause()

    renderer.handle_event(_click((390, 369)), controller)
    assert not controller.running

    controller = ScreenController()
    renderer.handle_event(pygame.event.Event(pygame.QUIT), controller)
    assert not controller.running


@pytest.mark.usefixtures("pygame_context")
def test_results_buttons_navigate_and_quit() -> None:
    renderer = ScreenRenderer()
    controller = _started_controller()
    controller.show_results()

    renderer.handle_event(_click((285, 535)), controller)
    assert controller.screen is ScreenState.PLAYER_SETUP

    controller.show_results()
    renderer.handle_event(_click((425, 535)), controller)
    assert controller.screen is ScreenState.MAIN_MENU

    controller.show_results()
    renderer.handle_event(_click((565, 535)), controller)
    assert not controller.running


def test_application_smoke_loop_initializes_and_exits() -> None:
    LudoApplication().run(smoke_frames=1)


def test_main_smoke_argument_runs() -> None:
    main(["--smoke"])


def _started_controller() -> ScreenController:
    controller = ScreenController()
    controller.open_setup()
    controller.update_name(0, "Alice")
    controller.update_name(1, "Bob")
    controller.start_game()
    return controller


def _click(position: tuple[int, int]) -> pygame.event.Event:
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": position})


def _key(key: int, unicode: str) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, {"key": key, "unicode": unicode})
