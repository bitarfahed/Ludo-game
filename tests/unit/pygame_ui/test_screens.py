"""Smoke tests for Pygame shell rendering and event dispatch."""

import os
from dataclasses import replace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from ludo.app import GameFacade
from ludo.domain import (
    FixedClock,
    FixedDice,
    Match,
    Piece,
    PieceState,
    PlayerColor,
    TurnPhase,
)
from ludo.domain.match import FixedColorRandomizer
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
    renderer.handle_event(_click((390, 325)), controller)
    assert controller.screen is ScreenState.MAIN_MENU


@pytest.mark.usefixtures("pygame_context")
def test_pause_quit_and_window_quit_signal_shutdown() -> None:
    renderer = ScreenRenderer()
    controller = _started_controller()
    controller.toggle_pause()

    renderer.handle_event(_click((390, 369)), controller)
    assert not controller.running


@pytest.mark.usefixtures("pygame_context")
def test_pause_restart_starts_clean_match() -> None:
    renderer = ScreenRenderer()
    controller = _started_controller()
    original_facade = controller.facade
    renderer.animation.start_dice(6)
    controller.toggle_pause()

    renderer.handle_event(_click((390, 275)), controller)

    assert controller.screen is ScreenState.GAME
    assert controller.facade is not original_facade
    assert not controller.paused
    assert not renderer.animation.input_locked

    controller = ScreenController()
    renderer.handle_event(pygame.event.Event(pygame.QUIT), controller)
    assert not controller.running


@pytest.mark.usefixtures("pygame_context")
def test_results_buttons_navigate_and_quit() -> None:
    renderer = ScreenRenderer()
    controller = _started_controller()
    controller.show_results()

    renderer.handle_event(_click((285, 535)), controller)
    assert controller.screen is ScreenState.GAME
    assert controller.facade is not None

    controller.show_results()
    renderer.animation.start_dice(6)
    renderer.handle_event(_click((425, 535)), controller)
    assert controller.screen is ScreenState.MAIN_MENU
    assert not renderer.animation.input_locked

    controller.show_results()
    renderer.handle_event(_click((565, 535)), controller)
    assert not controller.running


@pytest.mark.usefixtures("pygame_context")
def test_no_legal_move_notice_counts_down_and_passes_turn() -> None:
    renderer = ScreenRenderer()
    clock = FixedClock()
    controller = _deterministic_controller([1], clock=clock)

    dice_center = renderer.board_renderer.geometry.center_dice_area.center
    renderer.handle_event(_click(dice_center), controller)
    assert controller.no_legal_notice_ms_remaining == 5_000
    assert controller.snapshot().phase is TurnPhase.NO_LEGAL_MOVE

    renderer.update(5_000, controller)

    assert controller.no_legal_notice_ms_remaining == 0
    assert controller.snapshot().phase is TurnPhase.WAITING_FOR_ROLL
    assert controller.snapshot().current_player.color is PlayerColor.YELLOW


@pytest.mark.usefixtures("pygame_context")
def test_roll_timeout_feedback_and_transition() -> None:
    renderer = ScreenRenderer()
    clock = FixedClock()
    controller = _deterministic_controller([6], clock=clock)

    clock.advance(10)
    renderer.update(1, controller)

    assert controller.feedback_message == "ROLL TIMEOUT"
    assert controller.snapshot().current_player.color is PlayerColor.YELLOW


@pytest.mark.usefixtures("pygame_context")
def test_move_timeout_feedback_and_transition() -> None:
    renderer = ScreenRenderer()
    clock = FixedClock()
    controller = _deterministic_controller([6], clock=clock)
    controller.facade.roll()

    clock.advance(10)
    renderer.update(1, controller)

    assert controller.feedback_message == "MOVE TIMEOUT"
    assert controller.snapshot().current_player.color is PlayerColor.YELLOW


@pytest.mark.usefixtures("pygame_context")
def test_pause_freezes_timeout_and_animation_update() -> None:
    renderer = ScreenRenderer()
    clock = FixedClock()
    controller = _deterministic_controller([6], clock=clock)
    renderer.animation.start_dice(6)
    controller.toggle_pause()

    clock.advance(10)
    renderer.update(500, controller)

    assert controller.snapshot().current_player.color is PlayerColor.RED
    assert renderer.animation.dice is not None
    assert renderer.animation.dice.elapsed_ms == 0


@pytest.mark.usefixtures("pygame_context")
def test_resume_allows_timeout_to_continue() -> None:
    renderer = ScreenRenderer()
    clock = FixedClock()
    controller = _deterministic_controller([6], clock=clock)
    controller.toggle_pause()
    clock.advance(10)
    renderer.update(1, controller)
    controller.resume()

    renderer.update(1, controller)

    assert controller.feedback_message == "ROLL TIMEOUT"
    assert controller.snapshot().current_player.color is PlayerColor.YELLOW


@pytest.mark.usefixtures("pygame_context")
def test_ranking_notification_occurs_and_ranked_player_leaves_rotation() -> None:
    renderer = ScreenRenderer()
    controller = ScreenController()
    controller.screen = ScreenState.GAME
    controller.facade = _facade_with_finishing_piece(3)

    controller.facade.roll()
    result = controller.facade.choose_piece("red-final")
    renderer._process_result(result, controller)

    assert controller.feedback_message == "P1 finished! Rank 1"
    assert controller.snapshot().current_player.color is PlayerColor.GREEN
    assert PlayerColor.RED not in {
        player.color for player in controller.facade._match.turn_engine.players
    }


@pytest.mark.parametrize(
    ("player_count", "colors"),
    [
        (2, (PlayerColor.RED, PlayerColor.YELLOW)),
        (3, (PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW)),
        (4, (PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE)),
    ],
)
def test_results_rankings_support_player_counts(
    player_count: int, colors: tuple[PlayerColor, ...]
) -> None:
    match = _completed_match(player_count, colors)
    facade = GameFacade.from_match(match)

    assert [(entry.rank, entry.color) for entry in facade.rankings()] == [
        (index, color) for index, color in enumerate(colors, start=1)
    ]


@pytest.mark.usefixtures("pygame_context")
def test_representative_match_completion_flow_reaches_results() -> None:
    renderer = ScreenRenderer()
    controller = ScreenController()
    controller.screen = ScreenState.GAME
    controller.facade = _facade_with_finishing_piece(2)

    controller.facade.roll()
    result = controller.facade.choose_piece("red-final")
    renderer._process_result(result, controller)

    assert result.match_completed
    assert controller.screen is ScreenState.RESULTS


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


def _deterministic_controller(rolls: list[int], clock: FixedClock) -> ScreenController:
    controller = ScreenController()
    controller.screen = ScreenState.GAME
    controller.facade = GameFacade()
    controller.facade.start_match(
        ("Alice", "Bob"),
        color_randomizer=FixedColorRandomizer(
            choices=[(PlayerColor.RED, PlayerColor.YELLOW)],
            samples=[(PlayerColor.RED, PlayerColor.YELLOW)],
        ),
        dice=FixedDice(rolls),
        clock=clock,
    )
    return controller


def _facade_with_finishing_piece(player_count: int) -> GameFacade:
    colors = (
        (PlayerColor.RED, PlayerColor.YELLOW)
        if player_count == 2
        else (PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW)
    )
    match = _match_with_colors(player_count, colors)
    red = match.player_by_color(PlayerColor.RED)
    red = replace(
        red,
        pieces=(
            Piece("red-1", PlayerColor.RED, PieceState.FINISHED),
            Piece("red-2", PlayerColor.RED, PieceState.FINISHED),
            Piece("red-3", PlayerColor.RED, PieceState.FINISHED),
            Piece("red-final", PlayerColor.RED, PieceState.ON_HOME_PATH, 4),
        ),
    )
    match.turn_engine.replace_player(red)
    return GameFacade.from_match(match)


def _completed_match(player_count: int, colors: tuple[PlayerColor, ...]) -> Match:
    match = _match_with_colors(player_count, colors)
    for color in colors[:-1]:
        player = match.player_by_color(color)
        finished = replace(
            player,
            pieces=tuple(
                Piece(piece.id, color, PieceState.FINISHED) for piece in player.pieces
            ),
        )
        match.turn_engine.replace_player(finished)
        match.evaluate_rankings()
    return match


def _match_with_colors(player_count: int, colors: tuple[PlayerColor, ...]) -> Match:
    return Match.create(
        player_names=tuple(f"P{index}" for index in range(1, player_count + 1)),
        color_randomizer=FixedColorRandomizer(
            choices=[colors] if player_count == 2 else [],
            samples=[colors],
        ),
        dice=FixedDice([1, 1, 1, 1]),
        clock=FixedClock(),
    )


def _click(position: tuple[int, int]) -> pygame.event.Event:
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": position})


def _key(key: int, unicode: str) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, {"key": key, "unicode": unicode})
