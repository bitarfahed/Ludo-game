"""Unit tests for the core piece domain model."""

import pytest

from ludo.domain import Piece, PieceState, PlayerColor


def test_player_color_symbols_are_domain_identifiers_not_rendering_values() -> None:
    assert PlayerColor.RED.piece_symbol == "r"
    assert PlayerColor.GREEN.piece_symbol == "g"
    assert PlayerColor.YELLOW.piece_symbol == "y"
    assert PlayerColor.BLUE.piece_symbol == "b"


def test_new_piece_starts_in_yard_with_no_path_progress() -> None:
    piece = Piece(id="red-1", owner_color=PlayerColor.RED)

    assert piece.id == "red-1"
    assert piece.owner_color is PlayerColor.RED
    assert piece.state is PieceState.IN_YARD
    assert piece.path_progress is None


def test_active_piece_requires_non_negative_path_progress() -> None:
    piece = Piece(
        id="green-1",
        owner_color=PlayerColor.GREEN,
        state=PieceState.ON_OUTER_PATH,
        path_progress=0,
    )

    assert piece.path_progress == 0


@pytest.mark.parametrize("state", [PieceState.ON_OUTER_PATH, PieceState.ON_HOME_PATH])
def test_path_state_rejects_missing_progress(state: PieceState) -> None:
    with pytest.raises(ValueError, match="path progress"):
        Piece(id="blue-1", owner_color=PlayerColor.BLUE, state=state)


def test_path_state_rejects_negative_progress() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        Piece(
            id="yellow-1",
            owner_color=PlayerColor.YELLOW,
            state=PieceState.ON_HOME_PATH,
            path_progress=-1,
        )


@pytest.mark.parametrize("state", [PieceState.IN_YARD, PieceState.FINISHED])
def test_non_path_state_rejects_progress(state: PieceState) -> None:
    with pytest.raises(ValueError, match="path progress"):
        Piece(id="red-1", owner_color=PlayerColor.RED, state=state, path_progress=0)


def test_piece_rejects_blank_identifier() -> None:
    with pytest.raises(ValueError, match="identifier"):
        Piece(id=" ", owner_color=PlayerColor.RED)


def test_piece_rejects_invalid_owner_color() -> None:
    with pytest.raises(TypeError, match="owner_color"):
        Piece(id="red-1", owner_color="RED")  # type: ignore[arg-type]


def test_piece_rejects_invalid_state() -> None:
    with pytest.raises(TypeError, match="state"):
        Piece(
            id="red-1",
            owner_color=PlayerColor.RED,
            state="IN_YARD",  # type: ignore[arg-type]
        )
