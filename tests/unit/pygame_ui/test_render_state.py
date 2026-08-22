"""Tests for gameplay render-state preparation."""

from ludo.app import GameSnapshot, OuterOccupancySnapshot, PieceSnapshot, PlayerSnapshot
from ludo.domain import PieceState, PlayerColor, TurnPhase
from ludo.geometry import BoardGeometry
from ludo.pygame_ui.render_models import PieceLocationKind
from ludo.pygame_ui.render_state import (
    build_gameplay_render_state,
    build_occupancy_inspection,
)


def piece(
    piece_id: str,
    color: PlayerColor,
    state: PieceState = PieceState.IN_YARD,
    progress: int | None = None,
) -> PieceSnapshot:
    return PieceSnapshot(piece_id, color, state, progress)


def player(
    player_id: str,
    color: PlayerColor,
    pieces: tuple[PieceSnapshot, ...],
    rank: int | None = None,
) -> PlayerSnapshot:
    return PlayerSnapshot(player_id, player_id.title(), color, pieces, rank)


def snapshot(
    players: tuple[PlayerSnapshot, ...],
    current_player: PlayerSnapshot | None = None,
    phase: TurnPhase | None = TurnPhase.WAITING_FOR_ROLL,
    dice_value: int | None = None,
    seconds_remaining: int = 7,
    outer_occupancies: tuple[OuterOccupancySnapshot, ...] = (),
) -> GameSnapshot:
    return GameSnapshot(
        players=players,
        inactive_colors=frozenset(set(PlayerColor) - {player.color for player in players}),
        current_player=current_player,
        phase=phase,
        seconds_remaining=seconds_remaining,
        decision_timeout_seconds=10,
        current_dice_value=dice_value,
        legal_moves=(),
        outer_occupancies=outer_occupancies,
        rankings=(),
        is_complete=False,
    )


def progress_to_global(color: PlayerColor, global_index: int) -> int:
    return (global_index - BoardGeometry().topology.start_position(color)) % 52


def outer_piece(piece_id: str, color: PlayerColor, global_index: int) -> PieceSnapshot:
    return piece(
        piece_id,
        color,
        PieceState.ON_OUTER_PATH,
        progress_to_global(color, global_index),
    )


def test_yard_pieces_map_to_distinct_yard_slots() -> None:
    red = player(
        "red",
        PlayerColor.RED,
        tuple(piece(f"red-{index}", PlayerColor.RED) for index in range(4)),
    )

    state = build_gameplay_render_state(snapshot((red,), red), BoardGeometry())

    yard_groups = [
        group for group in state.pieces if group.pieces[0].location.kind is PieceLocationKind.YARD
    ]
    assert len(yard_groups) == 4
    assert {group.pieces[0].location.index for group in yard_groups} == {0, 1, 2, 3}


def test_outer_piece_maps_to_global_outer_square() -> None:
    geometry = BoardGeometry()
    red = player(
        "red",
        PlayerColor.RED,
        (piece("red-outer", PlayerColor.RED, PieceState.ON_OUTER_PATH, 8),),
    )

    state = build_gameplay_render_state(snapshot((red,), red), geometry)

    group = state.pieces[0]
    assert group.pieces[0].location.kind is PieceLocationKind.OUTER
    assert group.pieces[0].location.index == geometry.topology.global_outer_index(
        PlayerColor.RED, 8
    )
    assert group.center == geometry.outer_square(8).center


def test_home_path_piece_maps_to_private_home_square() -> None:
    geometry = BoardGeometry()
    blue = player(
        "blue",
        PlayerColor.BLUE,
        (piece("blue-home", PlayerColor.BLUE, PieceState.ON_HOME_PATH, 3),),
    )

    state = build_gameplay_render_state(snapshot((blue,), blue), geometry)

    group = state.pieces[0]
    assert group.pieces[0].location.kind is PieceLocationKind.HOME
    assert group.pieces[0].location.index == 3
    assert group.center == geometry.home_path_square(PlayerColor.BLUE, 3).center


def test_finished_piece_maps_to_finish_region_and_rank_status_is_represented() -> None:
    geometry = BoardGeometry()
    yellow = player(
        "yellow",
        PlayerColor.YELLOW,
        (piece("yellow-finished", PlayerColor.YELLOW, PieceState.FINISHED),),
        rank=1,
    )

    state = build_gameplay_render_state(snapshot((yellow,), None), geometry)

    assert state.pieces[0].pieces[0].location.kind is PieceLocationKind.FINISH
    assert state.pieces[0].center == geometry.finish_region(PlayerColor.YELLOW).center
    assert state.players[0].status_text == "Rank 1"


def test_single_piece_uses_normal_representation() -> None:
    red = player(
        "red",
        PlayerColor.RED,
        (piece("red-1", PlayerColor.RED, PieceState.ON_OUTER_PATH, 2),),
    )

    state = build_gameplay_render_state(snapshot((red,), red), BoardGeometry())

    assert len(state.pieces) == 1
    assert not state.pieces[0].is_stack_placeholder
    assert state.pieces[0].summary_components == ()


def test_same_color_stack_uses_compact_summary_components() -> None:
    red = player(
        "red",
        PlayerColor.RED,
        (
            piece("red-1", PlayerColor.RED, PieceState.ON_OUTER_PATH, 2),
            piece("red-2", PlayerColor.RED, PieceState.ON_OUTER_PATH, 2),
        ),
    )

    state = build_gameplay_render_state(snapshot((red,), red), BoardGeometry())

    assert len(state.pieces) == 1
    assert state.pieces[0].is_stack_placeholder
    assert [component.text for component in state.pieces[0].summary_components] == ["2r"]


def test_mixed_color_stack_uses_color_ordered_summary_components() -> None:
    red_piece = outer_piece("red-1", PlayerColor.RED, 2)
    blue_piece = outer_piece("blue-1", PlayerColor.BLUE, 2)
    red = player("red", PlayerColor.RED, (red_piece,))
    blue = player("blue", PlayerColor.BLUE, (blue_piece,))

    state = build_gameplay_render_state(snapshot((red, blue), red), BoardGeometry())

    assert len(state.pieces) == 1
    assert [component.text for component in state.pieces[0].summary_components] == [
        "1r",
        "1b",
    ]


def test_three_color_stack_summary_is_supported() -> None:
    red = player("red", PlayerColor.RED, (outer_piece("red-1", PlayerColor.RED, 2),))
    green = player(
        "green", PlayerColor.GREEN, (outer_piece("green-1", PlayerColor.GREEN, 2),)
    )
    yellow = player(
        "yellow", PlayerColor.YELLOW, (outer_piece("yellow-1", PlayerColor.YELLOW, 2),)
    )

    state = build_gameplay_render_state(snapshot((red, green, yellow), red), BoardGeometry())

    assert [component.text for component in state.pieces[0].summary_components] == [
        "1r",
        "1g",
        "1y",
    ]


def test_large_safe_square_stack_summary_and_safe_status_are_exposed() -> None:
    global_index = 0
    pieces = (
        outer_piece("red-1", PlayerColor.RED, global_index),
        outer_piece("red-2", PlayerColor.RED, global_index),
        outer_piece("green-1", PlayerColor.GREEN, global_index),
        outer_piece("yellow-1", PlayerColor.YELLOW, global_index),
        outer_piece("blue-1", PlayerColor.BLUE, global_index),
    )
    players = (
        player("red", PlayerColor.RED, pieces[:2]),
        player("green", PlayerColor.GREEN, (pieces[2],)),
        player("yellow", PlayerColor.YELLOW, (pieces[3],)),
        player("blue", PlayerColor.BLUE, (pieces[4],)),
    )
    occupancy = OuterOccupancySnapshot(global_index, pieces, is_safe=True, is_protected=True)

    state = build_gameplay_render_state(
        snapshot(players, players[0], outer_occupancies=(occupancy,)), BoardGeometry()
    )

    assert [component.text for component in state.pieces[0].summary_components] == [
        "2r",
        "1g",
        "1y",
        "1b",
    ]
    assert state.pieces[0].inspection is not None
    assert state.pieces[0].inspection.is_safe
    assert not state.pieces[0].inspection.is_protected


def test_protected_block_status_is_exposed_from_occupancy_snapshot() -> None:
    global_index = 2
    pieces = (
        outer_piece("red-1", PlayerColor.RED, global_index),
        outer_piece("red-2", PlayerColor.RED, global_index),
    )
    red = player("red", PlayerColor.RED, pieces)
    occupancy = OuterOccupancySnapshot(global_index, pieces, is_safe=False, is_protected=True)

    state = build_gameplay_render_state(
        snapshot((red,), red, outer_occupancies=(occupancy,)), BoardGeometry()
    )

    assert state.pieces[0].inspection is not None
    assert not state.pieces[0].inspection.is_safe
    assert state.pieces[0].inspection.is_protected


def test_safe_square_status_is_exposed_from_occupancy_snapshot() -> None:
    global_index = 0
    pieces = (outer_piece("red-1", PlayerColor.RED, global_index),)
    red = player("red", PlayerColor.RED, pieces)
    occupancy = OuterOccupancySnapshot(global_index, pieces, is_safe=True, is_protected=False)

    state = build_gameplay_render_state(
        snapshot((red,), red, outer_occupancies=(occupancy,)), BoardGeometry()
    )

    assert state.pieces[0].inspection is not None
    assert state.pieces[0].inspection.is_safe
    assert not state.pieces[0].inspection.is_protected


def test_hover_on_empty_square_produces_no_occupancy_popup() -> None:
    red = player("red", PlayerColor.RED, (outer_piece("red-1", PlayerColor.RED, 2),))

    inspection = build_occupancy_inspection(snapshot((red,), red), BoardGeometry(), (1, 1))

    assert inspection is None


def test_hover_on_occupied_square_shows_correct_counts() -> None:
    geometry = BoardGeometry()
    global_index = 2
    red_piece = outer_piece("red-1", PlayerColor.RED, global_index)
    blue_piece = outer_piece("blue-1", PlayerColor.BLUE, global_index)
    red = player("red", PlayerColor.RED, (red_piece,))
    blue = player("blue", PlayerColor.BLUE, (blue_piece,))

    inspection = build_occupancy_inspection(
        snapshot((red, blue), red),
        geometry,
        geometry.outer_square(global_index).center,
    )

    assert inspection is not None
    assert [(line.color_name, line.count) for line in inspection.lines] == [
        ("Red", 1),
        ("Blue", 1),
    ]


def test_popup_placement_remains_inside_representative_window_bounds() -> None:
    geometry = BoardGeometry()
    global_index = 23
    red_piece = outer_piece("red-1", PlayerColor.RED, global_index)
    red = player("red", PlayerColor.RED, (red_piece,))

    inspection = build_occupancy_inspection(
        snapshot((red,), red),
        geometry,
        geometry.outer_square(global_index).center,
    )

    assert inspection is not None
    assert inspection.popup.x >= 0
    assert inspection.popup.y >= 0
    assert inspection.popup.x + inspection.popup.width <= geometry.window_size[0]
    assert inspection.popup.y + inspection.popup.height <= geometry.window_size[1]


def test_current_dice_value_and_roll_availability_are_reflected() -> None:
    red = player("red", PlayerColor.RED, (piece("red-1", PlayerColor.RED),))

    roll_state = build_gameplay_render_state(snapshot((red,), red), BoardGeometry())
    move_state = build_gameplay_render_state(
        snapshot((red,), red, phase=TurnPhase.WAITING_FOR_MOVE, dice_value=5),
        BoardGeometry(),
    )

    assert roll_state.dice.current_value is None
    assert roll_state.dice.roll_available
    assert move_state.dice.current_value == 5
    assert not move_state.dice.roll_available


def test_current_player_and_timer_state_are_derived_from_snapshot() -> None:
    red = player("red", PlayerColor.RED, (piece("red-1", PlayerColor.RED),))
    blue = player("blue", PlayerColor.BLUE, (piece("blue-1", PlayerColor.BLUE),))

    state = build_gameplay_render_state(
        snapshot((red, blue), blue, seconds_remaining=4), BoardGeometry()
    )

    red_hud, blue_hud = state.players
    assert not red_hud.active
    assert red_hud.seconds_remaining is None
    assert blue_hud.active
    assert blue_hud.seconds_remaining == 4
    assert blue_hud.timer_progress == 0.4


def test_inactive_players_are_not_rendered_as_active_participants() -> None:
    red = player("red", PlayerColor.RED, (piece("red-1", PlayerColor.RED),))

    state = build_gameplay_render_state(snapshot((red,), red), BoardGeometry())

    assert [player_state.color_value for player_state in state.players] == ["red"]
