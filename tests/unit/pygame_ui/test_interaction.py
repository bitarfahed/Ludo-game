"""Tests for gameplay mouse interaction state."""

from dataclasses import replace

from ludo.app import GameFacade
from ludo.domain import (
    FixedClock,
    FixedDice,
    FixedHazardRandomizer,
    FixedSpecialDie,
    Match,
    Piece,
    PieceState,
    PlayerColor,
    TurnPhase,
)
from ludo.domain.match import FixedColorRandomizer
from ludo.geometry import BoardGeometry
from ludo.pygame_ui.animation import AnimationManager
from ludo.pygame_ui.interaction import GameplayInteractionController
from ludo.pygame_ui.state import ScreenController, ScreenState


def click_to_move_phase(
    interaction: GameplayInteractionController,
    geometry: BoardGeometry,
    controller: ScreenController,
) -> None:
    assert interaction.handle_click(geometry.center_dice_area.center, controller)
    interaction.animation.update(500)
    assert interaction.handle_click(geometry.special_die_area.center, controller)
    interaction.animation.update(500)


def started_controller(rolls: list[int]) -> ScreenController:
    controller = ScreenController()
    controller.screen = ScreenState.GAME
    controller.facade = GameFacade()
    controller.facade.start_match(
        ("Alice", "Bob"),
        color_randomizer=FixedColorRandomizer(
            choices=[(PlayerColor.RED, PlayerColor.YELLOW)],
            samples=[(PlayerColor.RED, PlayerColor.YELLOW)],
        ),
        hazard_randomizer=FixedHazardRandomizer([11, 24, 37, 50]),
        dice=FixedDice(rolls),
        special_die=FixedSpecialDie([0] * 20),
        clock=FixedClock(),
    )
    return controller


def test_dice_click_works_only_in_roll_phase_and_routes_through_facade() -> None:
    geometry = BoardGeometry()
    interaction = GameplayInteractionController(geometry)
    controller = started_controller([6, 3])

    assert interaction.handle_click(geometry.center_dice_area.center, controller)
    assert controller.facade.snapshot().phase is TurnPhase.WAITING_FOR_SPECIAL_ROLL
    assert controller.facade.snapshot().current_dice_value == 6

    assert not interaction.handle_click(geometry.center_dice_area.center, controller)
    assert controller.facade.snapshot().current_dice_value == 6


def test_legal_pieces_become_selectable_and_illegal_pieces_do_not() -> None:
    geometry = BoardGeometry()
    interaction = GameplayInteractionController(geometry)
    controller = started_controller([6])

    click_to_move_phase(interaction, geometry, controller)
    legal_ids = {move.piece_id for move in controller.facade.snapshot().legal_moves}

    assert legal_ids == {f"player-1-piece-{index}" for index in range(1, 5)}

    yellow_piece_point = geometry.yard_piece_positions(PlayerColor.YELLOW)[0]
    assert not interaction.handle_click(yellow_piece_point, controller)
    assert controller.facade.piece_state("player-2-piece-1").state is PieceState.IN_YARD


def test_one_legal_move_is_not_auto_selected() -> None:
    geometry = BoardGeometry()
    interaction = GameplayInteractionController(geometry)
    controller = controller_with_one_legal_outer_piece()

    click_to_move_phase(interaction, geometry, controller)
    snapshot = controller.facade.snapshot()

    assert len(snapshot.legal_moves) == 1
    assert controller.facade.piece_state("red-outer").path_progress == 0


def test_legal_piece_hover_exposes_destination_preview() -> None:
    geometry = BoardGeometry()
    interaction = GameplayInteractionController(geometry)
    controller = started_controller([6])

    click_to_move_phase(interaction, geometry, controller)
    interaction.handle_hover(geometry.yard_piece_positions(PlayerColor.RED)[0], controller)

    assert interaction.preview is not None
    assert interaction.preview.piece_id == "player-1-piece-1"
    assert interaction.preview.bounds == geometry.outer_square(0)
    assert interaction.preview.hint == "Use 6"


def test_legal_piece_click_submits_move_and_updates_ui_state() -> None:
    geometry = BoardGeometry()
    interaction = GameplayInteractionController(geometry)
    controller = started_controller([6])

    click_to_move_phase(interaction, geometry, controller)
    assert interaction.handle_click(geometry.yard_piece_positions(PlayerColor.RED)[0], controller)

    moved = controller.facade.piece_state("player-1-piece-1")
    assert moved.state is PieceState.ON_OUTER_PATH
    assert moved.path_progress == 0
    assert controller.facade.snapshot().phase is TurnPhase.WAITING_FOR_ROLL


def test_invalid_piece_click_and_outside_click_are_harmless() -> None:
    geometry = BoardGeometry()
    interaction = GameplayInteractionController(geometry)
    controller = started_controller([6])

    assert not interaction.handle_click((0, 0), controller)
    assert controller.facade.snapshot().phase is TurnPhase.WAITING_FOR_ROLL

    click_to_move_phase(interaction, geometry, controller)
    assert not interaction.handle_click(geometry.yard_region(PlayerColor.BLUE).center, controller)
    assert controller.facade.snapshot().phase is TurnPhase.WAITING_FOR_MOVE


def test_roll_phase_prevents_piece_move() -> None:
    geometry = BoardGeometry()
    interaction = GameplayInteractionController(geometry)
    controller = started_controller([6])

    assert not interaction.handle_click(
        geometry.yard_piece_positions(PlayerColor.RED)[0], controller
    )
    assert controller.facade.piece_state("player-1-piece-1").state is PieceState.IN_YARD


def test_repeated_piece_click_does_not_duplicate_action() -> None:
    geometry = BoardGeometry()
    interaction = GameplayInteractionController(geometry)
    controller = started_controller([6])
    piece_point = geometry.yard_piece_positions(PlayerColor.RED)[0]

    click_to_move_phase(interaction, geometry, controller)
    assert interaction.handle_click(piece_point, controller)
    assert not interaction.handle_click(piece_point, controller)

    assert controller.facade.piece_state("player-1-piece-1").path_progress == 0


def test_gameplay_action_cannot_execute_during_locked_animation() -> None:
    geometry = BoardGeometry()
    animation = AnimationManager()
    interaction = GameplayInteractionController(geometry, animation=animation)
    controller = started_controller([6])

    animation.start_dice(6)

    assert not interaction.handle_click(geometry.center_dice_area.center, controller)
    assert controller.facade.snapshot().phase is TurnPhase.WAITING_FOR_ROLL


def test_no_legal_roll_disables_piece_interaction() -> None:
    geometry = BoardGeometry()
    interaction = GameplayInteractionController(geometry)
    controller = started_controller([1])

    click_to_move_phase(interaction, geometry, controller)

    assert controller.facade.snapshot().phase is TurnPhase.NO_LEGAL_MOVE
    assert controller.facade.snapshot().legal_moves == ()
    assert not interaction.handle_click(
        geometry.yard_piece_positions(PlayerColor.RED)[0], controller
    )


def controller_with_one_legal_outer_piece() -> ScreenController:
    match = Match.create(
        ("Alice", "Bob"),
        color_randomizer=FixedColorRandomizer(
            choices=[(PlayerColor.RED, PlayerColor.YELLOW)],
            samples=[(PlayerColor.RED, PlayerColor.YELLOW)],
        ),
        hazard_randomizer=FixedHazardRandomizer([11, 24, 37, 50]),
        dice=FixedDice([3]),
        special_die=FixedSpecialDie([0] * 20),
        clock=FixedClock(),
    )
    red = match.player_by_color(PlayerColor.RED)
    pieces = (
        Piece("red-outer", PlayerColor.RED, PieceState.ON_OUTER_PATH, 0),
        Piece("red-finished-1", PlayerColor.RED, PieceState.FINISHED),
        Piece("red-finished-2", PlayerColor.RED, PieceState.FINISHED),
        Piece("red-finished-3", PlayerColor.RED, PieceState.FINISHED),
    )
    match.turn_engine.replace_player(replace(red, pieces=pieces))
    controller = ScreenController()
    controller.screen = ScreenState.GAME
    controller.facade = GameFacade.from_match(match)
    return controller
