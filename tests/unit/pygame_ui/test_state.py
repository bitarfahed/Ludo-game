"""Tests for Pygame screen-flow state independent from rendering."""

import pytest

from ludo.app import GameFacade
from ludo.pygame_ui.state import MAX_PLAYER_COUNT, MIN_PLAYER_COUNT, ScreenController, ScreenState


def named_controller() -> ScreenController:
    controller = ScreenController()
    controller.open_setup()
    controller.update_name(0, "Alice")
    controller.update_name(1, "Bob")
    return controller


def test_starts_on_main_menu() -> None:
    controller = ScreenController()

    assert controller.screen is ScreenState.MAIN_MENU
    assert controller.running


def test_main_menu_can_open_player_setup_and_back() -> None:
    controller = ScreenController()

    controller.open_setup()
    controller.back_to_menu()

    assert controller.screen is ScreenState.MAIN_MENU
    assert controller.facade is None


@pytest.mark.parametrize("player_count", [MIN_PLAYER_COUNT, 3, MAX_PLAYER_COUNT])
def test_valid_player_count_selection_resizes_name_fields(player_count: int) -> None:
    controller = ScreenController()

    controller.set_player_count(player_count)

    assert controller.setup.player_count == player_count
    assert len(controller.setup.names) == player_count


def test_invalid_player_count_is_rejected() -> None:
    controller = ScreenController()

    with pytest.raises(ValueError, match="2, 3, or 4"):
        controller.set_player_count(5)


def test_name_input_is_limited_to_ten_characters() -> None:
    controller = ScreenController()

    controller.update_name(0, "LongPlayerName")

    assert controller.setup.names[0] == "LongPlayer"


def test_blank_names_prevent_starting_game() -> None:
    controller = ScreenController()
    controller.open_setup()
    controller.update_name(0, "Alice")

    with pytest.raises(ValueError, match="blank"):
        controller.start_game()

    assert controller.screen is ScreenState.PLAYER_SETUP
    assert controller.error_message == "Enter a name for every player."


def test_start_game_creates_match_through_facade() -> None:
    controller = named_controller()

    snapshot = controller.start_game()

    assert controller.screen is ScreenState.GAME
    assert isinstance(controller.facade, GameFacade)
    assert {player.name for player in snapshot.players} == {"Alice", "Bob"}


def test_pause_toggles_only_on_game_screen() -> None:
    controller = ScreenController()

    controller.toggle_pause()
    assert not controller.paused

    named_controller().start_game()
    controller = named_controller()
    controller.start_game()
    controller.toggle_pause()
    assert controller.paused
    controller.resume()
    assert not controller.paused


def test_results_navigation() -> None:
    controller = named_controller()
    controller.start_game()

    controller.show_results()
    controller.play_again()

    assert controller.screen is ScreenState.GAME
    assert controller.facade is not None


def test_quit_signals_application_shutdown() -> None:
    controller = ScreenController()

    controller.quit()

    assert not controller.running
