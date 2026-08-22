"""Unit tests for the logical Ludo board topology."""

import pytest

from ludo.domain import BoardTopology, HomePathPosition, PlayerColor
from ludo.domain.board import HOME_PATH_LENGTH, OUTER_PATH_LENGTH


def test_topology_sizes_and_invariants() -> None:
    topology = BoardTopology()

    assert len(topology.outer_positions) == OUTER_PATH_LENGTH == 52
    assert len(topology.start_positions) == 4
    assert len(topology.safe_outer_positions) == 8
    assert topology.safe_outer_positions.issuperset(topology.start_positions.values())


def test_start_positions_for_all_four_colors() -> None:
    topology = BoardTopology()

    assert topology.start_position(PlayerColor.RED) == 0
    assert topology.start_position(PlayerColor.GREEN) == 13
    assert topology.start_position(PlayerColor.YELLOW) == 26
    assert topology.start_position(PlayerColor.BLUE) == 39


def test_safe_square_membership() -> None:
    topology = BoardTopology()

    assert topology.safe_outer_positions == frozenset({0, 8, 13, 21, 26, 34, 39, 47})
    assert topology.is_safe_outer_position(0)
    assert topology.is_safe_outer_position(47)
    assert not topology.is_safe_outer_position(1)


@pytest.mark.parametrize("color", list(PlayerColor))
def test_all_starts_are_safe(color: PlayerColor) -> None:
    topology = BoardTopology()

    assert topology.is_safe_outer_position(topology.start_position(color))


@pytest.mark.parametrize(
    ("color", "expected_start"),
    [
        (PlayerColor.RED, 0),
        (PlayerColor.GREEN, 13),
        (PlayerColor.YELLOW, 26),
        (PlayerColor.BLUE, 39),
    ],
)
def test_relative_outer_progress_maps_to_global_start(
    color: PlayerColor, expected_start: int
) -> None:
    topology = BoardTopology()

    assert topology.global_outer_index(color, relative_progress=0) == expected_start


@pytest.mark.parametrize(
    ("color", "relative_progress", "expected_global"),
    [
        (PlayerColor.RED, 51, 51),
        (PlayerColor.GREEN, 51, 12),
        (PlayerColor.YELLOW, 51, 25),
        (PlayerColor.BLUE, 51, 38),
    ],
)
def test_mapping_near_end_of_outer_journey(
    color: PlayerColor, relative_progress: int, expected_global: int
) -> None:
    topology = BoardTopology()

    assert topology.global_outer_index(color, relative_progress) == expected_global


def test_global_index_wraparound() -> None:
    topology = BoardTopology()

    assert topology.global_outer_index(PlayerColor.BLUE, relative_progress=13) == 0
    assert topology.global_outer_index(PlayerColor.YELLOW, relative_progress=30) == 4


@pytest.mark.parametrize("relative_progress", [-1, 52])
def test_invalid_relative_outer_progress_is_rejected(relative_progress: int) -> None:
    topology = BoardTopology()

    with pytest.raises(ValueError, match="relative outer progress"):
        topology.global_outer_index(PlayerColor.RED, relative_progress)


@pytest.mark.parametrize("global_index", [-1, 52])
def test_invalid_global_outer_index_is_rejected(global_index: int) -> None:
    topology = BoardTopology()

    with pytest.raises(ValueError, match="global outer index"):
        topology.is_safe_outer_position(global_index)


@pytest.mark.parametrize("color", list(PlayerColor))
def test_home_path_length_for_every_color(color: PlayerColor) -> None:
    topology = BoardTopology()

    home_path = topology.home_path(color)

    assert len(home_path) == HOME_PATH_LENGTH == 5
    assert home_path == tuple(HomePathPosition(color=color, index=index) for index in range(5))


@pytest.mark.parametrize("color", list(PlayerColor))
def test_finished_destination_is_separate_from_home_path(color: PlayerColor) -> None:
    topology = BoardTopology()

    home_path = topology.home_path(color)
    finished = topology.finished_destination(color)

    assert finished.color is color
    assert finished not in home_path


def test_invalid_color_is_rejected() -> None:
    topology = BoardTopology()

    with pytest.raises(TypeError, match="PlayerColor"):
        topology.start_position("red")  # type: ignore[arg-type]
