"""Tests for logical-to-screen board geometry."""

from ludo.domain import BoardTopology, PlayerColor
from ludo.domain.board import HOME_PATH_LENGTH, OUTER_PATH_LENGTH
from ludo.geometry import BoardGeometry, BoardHitKind
from ludo.geometry.grid import OUTER_GRID_PATH

CORNER_TRANSITIONS = {
    5: ((5, 6), (6, 5)),
    18: ((8, 5), (9, 6)),
    31: ((9, 8), (8, 9)),
    44: ((6, 9), (5, 8)),
}

HOME_ENTRY_OUTER_INDICES = {
    PlayerColor.RED: 51,
    PlayerColor.GREEN: 12,
    PlayerColor.YELLOW: 25,
    PlayerColor.BLUE: 38,
}


def test_generates_52_distinct_outer_positions() -> None:
    geometry = BoardGeometry()

    assert len(geometry.outer_squares) == OUTER_PATH_LENGTH
    assert set(geometry.outer_squares) == set(range(OUTER_PATH_LENGTH))
    assert len({rect.center for rect in geometry.outer_squares.values()}) == OUTER_PATH_LENGTH


def test_outer_grid_path_has_unique_ordered_52_square_topology() -> None:
    assert len(OUTER_GRID_PATH) == OUTER_PATH_LENGTH
    assert len(set(OUTER_GRID_PATH)) == OUTER_PATH_LENGTH
    for start, end in zip(
        OUTER_GRID_PATH,
        (*OUTER_GRID_PATH[1:], OUTER_GRID_PATH[0]),
        strict=True,
    ):
        column_delta = abs(end[0] - start[0])
        row_delta = abs(end[1] - start[1])
        assert max(column_delta, row_delta) == 1
        assert column_delta + row_delta in {1, 2}


def test_outer_grid_path_corner_transitions_are_intentional_single_steps() -> None:
    for start_index, transition in CORNER_TRANSITIONS.items():
        assert OUTER_GRID_PATH[start_index : start_index + 2] == transition


def test_generates_five_home_path_positions_per_color() -> None:
    geometry = BoardGeometry()

    for color in PlayerColor:
        home_squares = geometry.home_path_squares(color)
        assert len(home_squares) == HOME_PATH_LENGTH
        assert len({rect.center for rect in home_squares}) == HOME_PATH_LENGTH


def test_has_four_yard_regions_and_four_finish_regions() -> None:
    geometry = BoardGeometry()

    yards = {color: geometry.yard_region(color) for color in PlayerColor}
    finishes = {color: geometry.finish_region(color) for color in PlayerColor}

    assert len(yards) == 4
    assert len(finishes) == 4
    assert all(region.width > 0 and region.height > 0 for region in yards.values())
    assert all(region.width > 0 and region.height > 0 for region in finishes.values())


def test_safe_square_positions_match_domain_topology() -> None:
    topology = BoardTopology()
    geometry = BoardGeometry(topology=topology)

    assert set(geometry.safe_squares) == topology.safe_outer_positions
    assert len(geometry.safe_squares) == 8


def test_start_positions_map_to_outer_squares() -> None:
    geometry = BoardGeometry()

    for color in PlayerColor:
        start_index = geometry.topology.start_position(color)
        assert geometry.outer_square(start_index) == geometry.safe_squares[start_index]


def test_outer_to_home_entry_is_geometrically_continuous_for_every_color() -> None:
    geometry = BoardGeometry()

    for color, outer_index in HOME_ENTRY_OUTER_INDICES.items():
        outer = geometry.outer_square(outer_index)
        home = geometry.home_path_square(color, 0)
        column_delta = abs(home.center[0] - outer.center[0]) // geometry.cell_size
        row_delta = abs(home.center[1] - outer.center[1]) // geometry.cell_size

        assert (column_delta, row_delta) in {(1, 0), (0, 1)}


def test_required_board_regions_are_inside_board_or_window() -> None:
    geometry = BoardGeometry()
    board = geometry.board_rect

    for rect in geometry.outer_squares.values():
        assert board.contains(rect.center)
    for color in PlayerColor:
        assert board.contains(geometry.yard_region(color).center)
        assert board.contains(geometry.finish_region(color).center)
        assert board.contains(geometry.player_label_area(color).center)
        assert board.contains(geometry.timer_area(color).center)
        assert len(geometry.yard_piece_positions(color)) == 4
    assert board.contains(geometry.center_dice_area.center)


def test_hit_testing_outer_square_from_representative_center() -> None:
    geometry = BoardGeometry()

    hit = geometry.hit_test(geometry.outer_square(21).center)

    assert hit is not None
    assert hit.kind is BoardHitKind.OUTER
    assert hit.outer_index == 21


def test_hit_testing_home_path_from_representative_center() -> None:
    geometry = BoardGeometry()

    hit = geometry.hit_test(geometry.home_path_square(PlayerColor.BLUE, 2).center)

    assert hit is not None
    assert hit.kind is BoardHitKind.HOME_PATH
    assert hit.color is PlayerColor.BLUE
    assert hit.home_index == 2


def test_hit_testing_yard_finish_dice_and_empty_space() -> None:
    geometry = BoardGeometry()

    yard_hit = geometry.hit_test(geometry.yard_region(PlayerColor.GREEN).center)
    finish_hit = geometry.hit_test(geometry.finish_region(PlayerColor.RED).center)
    dice_hit = geometry.hit_test(geometry.center_dice_area.center)

    assert yard_hit is not None
    assert yard_hit.kind is BoardHitKind.YARD
    assert yard_hit.color is PlayerColor.GREEN
    assert finish_hit is not None
    assert finish_hit.kind is BoardHitKind.FINISH
    assert finish_hit.color is PlayerColor.RED
    assert dice_hit is not None
    assert dice_hit.kind is BoardHitKind.DICE
    assert geometry.hit_test((0, 0)) is None


def test_geometry_adapts_to_window_size_while_staying_centered() -> None:
    geometry = BoardGeometry(window_size=(1200, 800), board_size=600)

    assert geometry.board_rect.x == 300
    assert geometry.board_rect.y == 100
    assert geometry.cell_size == 40
