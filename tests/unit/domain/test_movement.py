"""Unit tests for basic movement and legal-move calculation."""

from dataclasses import replace

import pytest

from ludo.domain import (
    BoardTopology,
    HomePathPosition,
    MoveDestination,
    MovementRules,
    Piece,
    PieceState,
    Player,
    PlayerColor,
)
from ludo.domain.movement import DiceValueError


def test_yard_piece_leaves_only_on_six_to_owner_start() -> None:
    piece = Piece(id="red-1", owner_color=PlayerColor.RED)
    rules = MovementRules()

    result = rules.propose_move(piece, dice_value=6)

    assert result is not None
    assert result.piece == replace(piece, state=PieceState.ON_OUTER_PATH, path_progress=0)
    assert result.destination == MoveDestination.outer(PlayerColor.RED, 0, 0)


@pytest.mark.parametrize("dice_value", [1, 2, 3, 4, 5])
def test_yard_piece_cannot_leave_without_six(dice_value: int) -> None:
    piece = Piece(id="red-1", owner_color=PlayerColor.RED)

    assert MovementRules().propose_move(piece, dice_value) is None


def test_normal_outer_path_movement_uses_relative_progress() -> None:
    piece = Piece(
        id="green-1",
        owner_color=PlayerColor.GREEN,
        state=PieceState.ON_OUTER_PATH,
        path_progress=10,
    )

    result = MovementRules().propose_move(piece, dice_value=4)

    assert result is not None
    assert result.piece.path_progress == 14
    assert result.piece.state is PieceState.ON_OUTER_PATH
    assert result.destination == MoveDestination.outer(PlayerColor.GREEN, 14, 27)


def test_outer_path_movement_near_end_remains_on_outer_path() -> None:
    piece = Piece(
        id="blue-1",
        owner_color=PlayerColor.BLUE,
        state=PieceState.ON_OUTER_PATH,
        path_progress=48,
    )

    result = MovementRules().propose_move(piece, dice_value=3)

    assert result is not None
    assert result.piece.path_progress == 51
    assert result.destination == MoveDestination.outer(PlayerColor.BLUE, 51, 38)


def test_outer_path_movement_can_cross_into_home_path() -> None:
    piece = Piece(
        id="yellow-1",
        owner_color=PlayerColor.YELLOW,
        state=PieceState.ON_OUTER_PATH,
        path_progress=50,
    )

    result = MovementRules().propose_move(piece, dice_value=4)

    assert result is not None
    assert result.piece == replace(piece, state=PieceState.ON_HOME_PATH, path_progress=2)
    assert result.destination == MoveDestination.home(HomePathPosition(PlayerColor.YELLOW, 2))


def test_outer_path_exactly_enters_first_home_path_square() -> None:
    piece = Piece(
        id="red-1",
        owner_color=PlayerColor.RED,
        state=PieceState.ON_OUTER_PATH,
        path_progress=51,
    )

    result = MovementRules().propose_move(piece, dice_value=1)

    assert result is not None
    assert result.piece.state is PieceState.ON_HOME_PATH
    assert result.piece.path_progress == 0


def test_movement_within_home_path() -> None:
    piece = Piece(
        id="green-1",
        owner_color=PlayerColor.GREEN,
        state=PieceState.ON_HOME_PATH,
        path_progress=1,
    )

    result = MovementRules().propose_move(piece, dice_value=3)

    assert result is not None
    assert result.piece.path_progress == 4
    assert result.destination == MoveDestination.home(HomePathPosition(PlayerColor.GREEN, 4))


def test_exact_home_path_move_reaches_finished() -> None:
    piece = Piece(
        id="blue-1",
        owner_color=PlayerColor.BLUE,
        state=PieceState.ON_HOME_PATH,
        path_progress=4,
    )

    result = MovementRules().propose_move(piece, dice_value=1)

    assert result is not None
    assert result.piece == replace(piece, state=PieceState.FINISHED, path_progress=None)
    assert result.destination == MoveDestination.finished(PlayerColor.BLUE)


def test_overshooting_finished_is_illegal() -> None:
    piece = Piece(
        id="red-1",
        owner_color=PlayerColor.RED,
        state=PieceState.ON_HOME_PATH,
        path_progress=4,
    )

    assert MovementRules().propose_move(piece, dice_value=6) is None


def test_outer_path_can_reach_finished_with_exact_roll() -> None:
    piece = Piece(
        id="red-1",
        owner_color=PlayerColor.RED,
        state=PieceState.ON_OUTER_PATH,
        path_progress=51,
    )

    result = MovementRules().propose_move(piece, dice_value=6)

    assert result is not None
    assert result.piece.state is PieceState.FINISHED
    assert result.piece.path_progress is None


def test_finished_piece_has_no_legal_move() -> None:
    piece = Piece(id="red-1", owner_color=PlayerColor.RED, state=PieceState.FINISHED)

    assert MovementRules().propose_move(piece, dice_value=1) is None


@pytest.mark.parametrize("dice_value", [0, 9])
def test_invalid_dice_values_are_rejected(dice_value: int) -> None:
    piece = Piece(id="red-1", owner_color=PlayerColor.RED)

    with pytest.raises(DiceValueError, match="movement value"):
        MovementRules().propose_move(piece, dice_value)


def test_legal_pieces_returns_only_pieces_that_can_use_dice_value() -> None:
    legal_home_piece = Piece(
        id="red-home",
        owner_color=PlayerColor.RED,
        state=PieceState.ON_HOME_PATH,
        path_progress=2,
    )
    finished_piece = Piece(
        id="red-finished",
        owner_color=PlayerColor.RED,
        state=PieceState.FINISHED,
    )
    yard_piece = Piece(id="red-yard", owner_color=PlayerColor.RED)
    overshooting_piece = Piece(
        id="red-overshoot",
        owner_color=PlayerColor.RED,
        state=PieceState.ON_HOME_PATH,
        path_progress=4,
    )
    player = Player(
        id="player-1",
        name="Alice",
        color=PlayerColor.RED,
        pieces=(legal_home_piece, finished_piece, yard_piece, overshooting_piece),
    )

    legal_pieces = MovementRules().legal_pieces(player, dice_value=2)

    assert legal_pieces == (legal_home_piece,)


def test_no_legal_pieces_returns_empty_tuple() -> None:
    player = Player(id="player-1", name="Alice", color=PlayerColor.RED)

    assert MovementRules().legal_pieces(player, dice_value=3) == ()


def test_all_four_yard_pieces_are_legal_on_six() -> None:
    player = Player(id="player-1", name="Alice", color=PlayerColor.RED)

    assert MovementRules().legal_pieces(player, dice_value=6) == player.pieces


def test_resolve_move_returns_moved_piece_for_legal_move() -> None:
    piece = Piece(id="red-1", owner_color=PlayerColor.RED)

    moved_piece = MovementRules().resolve_move(piece, dice_value=6)

    assert moved_piece == replace(piece, state=PieceState.ON_OUTER_PATH, path_progress=0)


def test_resolve_move_rejects_illegal_move() -> None:
    piece = Piece(id="red-1", owner_color=PlayerColor.RED)

    with pytest.raises(ValueError, match="legal move"):
        MovementRules().resolve_move(piece, dice_value=1)


def test_movement_rules_accept_custom_topology_for_global_destination() -> None:
    topology = BoardTopology(
        start_positions={color: index for index, color in enumerate(PlayerColor)}
    )
    piece = Piece(id="blue-1", owner_color=PlayerColor.BLUE)

    result = MovementRules(topology=topology).propose_move(piece, dice_value=6)

    assert result is not None
    assert result.destination == MoveDestination.outer(PlayerColor.BLUE, 0, 3)
