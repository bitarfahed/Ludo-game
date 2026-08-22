"""Unit tests for the core player domain model."""

import pytest

from ludo.domain import Piece, PieceState, Player, PlayerColor


def test_valid_player_creation_builds_four_yard_pieces() -> None:
    player = Player(id="player-1", name="Alice", color=PlayerColor.RED)

    assert player.id == "player-1"
    assert player.name == "Alice"
    assert player.color is PlayerColor.RED
    assert len(player.pieces) == 4
    assert {piece.owner_color for piece in player.pieces} == {PlayerColor.RED}
    assert {piece.state for piece in player.pieces} == {PieceState.IN_YARD}
    assert {piece.path_progress for piece in player.pieces} == {None}


def test_player_piece_identifiers_are_unique_and_stable() -> None:
    player = Player(id="player-1", name="Alice", color=PlayerColor.GREEN)

    piece_ids = [piece.id for piece in player.pieces]

    assert piece_ids == [
        "player-1-piece-1",
        "player-1-piece-2",
        "player-1-piece-3",
        "player-1-piece-4",
    ]
    assert len(set(piece_ids)) == 4


@pytest.mark.parametrize("name", ["A", "TenLetters"])
def test_player_accepts_valid_names_up_to_ten_characters(name: str) -> None:
    player = Player(id="player-1", name=name, color=PlayerColor.BLUE)

    assert player.name == name


def test_player_strips_surrounding_name_whitespace() -> None:
    player = Player(id="player-1", name="  Alice  ", color=PlayerColor.YELLOW)

    assert player.name == "Alice"


def test_player_rejects_names_longer_than_ten_characters() -> None:
    with pytest.raises(ValueError, match="10 characters"):
        Player(id="player-1", name="ElevenChars", color=PlayerColor.RED)


@pytest.mark.parametrize("name", ["", "   "])
def test_player_rejects_blank_names(name: str) -> None:
    with pytest.raises(ValueError, match="name"):
        Player(id="player-1", name=name, color=PlayerColor.RED)


def test_player_rejects_blank_identifier() -> None:
    with pytest.raises(ValueError, match="identifier"):
        Player(id="", name="Alice", color=PlayerColor.RED)


def test_player_rejects_invalid_color() -> None:
    with pytest.raises(TypeError, match="color"):
        Player(id="player-1", name="Alice", color="RED")  # type: ignore[arg-type]


def test_player_rejects_wrong_piece_count() -> None:
    pieces = (Piece(id="p1", owner_color=PlayerColor.RED),)

    with pytest.raises(ValueError, match="exactly four"):
        Player(id="player-1", name="Alice", color=PlayerColor.RED, pieces=pieces)


def test_player_rejects_piece_owned_by_another_color() -> None:
    pieces = tuple(Piece(id=f"p{i}", owner_color=PlayerColor.RED) for i in range(1, 4))
    pieces += (Piece(id="p4", owner_color=PlayerColor.BLUE),)

    with pytest.raises(ValueError, match="assigned color"):
        Player(id="player-1", name="Alice", color=PlayerColor.RED, pieces=pieces)


def test_player_rejects_duplicate_piece_identifiers() -> None:
    pieces = tuple(Piece(id="duplicate", owner_color=PlayerColor.RED) for _ in range(4))

    with pytest.raises(ValueError, match="unique"):
        Player(id="player-1", name="Alice", color=PlayerColor.RED, pieces=pieces)
