"""Unit tests for capture and protected outer-square occupancy."""

from dataclasses import replace

import pytest

from ludo.domain import (
    CollisionResolver,
    HomePathPosition,
    MoveDestination,
    MovementRules,
    OuterPathOccupancy,
    Piece,
    PieceState,
    PlayerColor,
)


def outer_piece(piece_id: str, color: PlayerColor, progress: int) -> Piece:
    return Piece(
        id=piece_id,
        owner_color=color,
        state=PieceState.ON_OUTER_PATH,
        path_progress=progress,
    )


def moving_to(global_index: int, color: PlayerColor = PlayerColor.BLUE):
    piece = outer_piece(f"{color.value}-moving", color, 0)
    moved_piece = replace(piece, path_progress=1)
    return replace(
        MovementRules().propose_move(piece, dice_value=1),
        piece=moved_piece,
        destination=MoveDestination.outer(color, 1, global_index),
    )


def test_vulnerable_opponent_is_captured_on_ordinary_square() -> None:
    red_piece = outer_piece("red-1", PlayerColor.RED, 1)
    occupancy = OuterPathOccupancy(global_index=1, pieces=(red_piece,))

    outcome = CollisionResolver().resolve(moving_to(1), occupancy)

    assert outcome.captured_piece == replace(
        red_piece, state=PieceState.IN_YARD, path_progress=None
    )
    assert outcome.capture_occurred
    assert outcome.destination_occupancy.pieces == (outcome.moved_piece,)
    assert not outcome.destination_protected


def test_own_single_piece_does_not_capture_itself() -> None:
    blue_piece = outer_piece("blue-1", PlayerColor.BLUE, 1)
    occupancy = OuterPathOccupancy(global_index=1, pieces=(blue_piece,))

    outcome = CollisionResolver().resolve(moving_to(1, PlayerColor.BLUE), occupancy)

    assert not outcome.capture_occurred
    assert outcome.destination_occupancy.pieces == (blue_piece, outcome.moved_piece)
    assert outcome.destination_protected


def test_two_same_color_pieces_create_protection() -> None:
    occupancy = OuterPathOccupancy(
        global_index=2,
        pieces=(
            outer_piece("red-1", PlayerColor.RED, 2),
            outer_piece("red-2", PlayerColor.RED, 2),
        ),
    )

    assert CollisionResolver().is_protected_occupancy(occupancy)


def test_protected_same_color_block_cannot_be_captured_and_can_be_joined() -> None:
    red_block = OuterPathOccupancy(
        global_index=2,
        pieces=(
            outer_piece("red-1", PlayerColor.RED, 2),
            outer_piece("red-2", PlayerColor.RED, 2),
        ),
    )

    outcome = CollisionResolver().resolve(moving_to(2), red_block)

    assert outcome.captured_piece is None
    assert outcome.destination_occupancy.pieces == (*red_block.pieces, outcome.moved_piece)
    assert outcome.destination_protected


def test_opponent_may_pass_through_block_without_interference() -> None:
    red_block = OuterPathOccupancy(
        global_index=2,
        pieces=(
            outer_piece("red-1", PlayerColor.RED, 2),
            outer_piece("red-2", PlayerColor.RED, 2),
        ),
    )
    proposal = moving_to(3)

    outcome = CollisionResolver().resolve(proposal, red_block)

    assert outcome.captured_piece is None
    assert outcome.destination_occupancy.pieces == (proposal.piece,)
    assert red_block.pieces[0].state is PieceState.ON_OUTER_PATH


def test_red_red_blue_forms_legal_protected_occupancy() -> None:
    red_block = OuterPathOccupancy(
        global_index=2,
        pieces=(
            outer_piece("red-1", PlayerColor.RED, 2),
            outer_piece("red-2", PlayerColor.RED, 2),
        ),
    )

    outcome = CollisionResolver().resolve(moving_to(2), red_block)

    assert [piece.owner_color for piece in outcome.destination_occupancy.pieces] == [
        PlayerColor.RED,
        PlayerColor.RED,
        PlayerColor.BLUE,
    ]
    assert outcome.destination_occupancy.was_protected


def test_red_blue_remains_protected_after_one_red_leaves() -> None:
    occupancy = OuterPathOccupancy(
        global_index=2,
        pieces=(
            outer_piece("red-1", PlayerColor.RED, 2),
            outer_piece("blue-1", PlayerColor.BLUE, 2),
        ),
        was_protected=True,
    )

    assert CollisionResolver().is_protected_occupancy(occupancy)


def test_mixed_block_with_three_colors_remains_protected() -> None:
    occupancy = OuterPathOccupancy(
        global_index=4,
        pieces=(
            outer_piece("red-1", PlayerColor.RED, 4),
            outer_piece("blue-1", PlayerColor.BLUE, 4),
            outer_piece("green-1", PlayerColor.GREEN, 4),
        ),
        was_protected=True,
    )

    assert CollisionResolver().is_protected_occupancy(occupancy)


def test_protection_disappears_when_ordinary_occupancy_drops_to_one_piece() -> None:
    occupancy = OuterPathOccupancy(
        global_index=2,
        pieces=(outer_piece("red-1", PlayerColor.RED, 2),),
        was_protected=True,
    )

    assert not CollisionResolver().is_protected_occupancy(occupancy)


def test_newly_vulnerable_remaining_piece_can_later_be_captured() -> None:
    red_piece = outer_piece("red-1", PlayerColor.RED, 2)
    occupancy = OuterPathOccupancy(global_index=2, pieces=(red_piece,), was_protected=True)

    outcome = CollisionResolver().resolve(moving_to(2), occupancy)

    assert outcome.captured_piece == replace(
        red_piece, state=PieceState.IN_YARD, path_progress=None
    )


def test_two_vulnerable_opponents_cannot_directly_create_mixed_block() -> None:
    red_piece = outer_piece("red-1", PlayerColor.RED, 2)
    occupancy = OuterPathOccupancy(global_index=2, pieces=(red_piece,))

    outcome = CollisionResolver().resolve(moving_to(2), occupancy)

    assert outcome.destination_occupancy.pieces == (outcome.moved_piece,)
    assert not outcome.destination_occupancy.was_protected


@pytest.mark.parametrize("safe_index", [0, 8])
def test_no_capture_on_start_or_star_safe_square(safe_index: int) -> None:
    red_piece = outer_piece("red-1", PlayerColor.RED, safe_index)
    occupancy = OuterPathOccupancy(global_index=safe_index, pieces=(red_piece,))

    outcome = CollisionResolver().resolve(moving_to(safe_index), occupancy)

    assert outcome.captured_piece is None
    assert outcome.destination_occupancy.pieces == (red_piece, outcome.moved_piece)
    assert outcome.destination_protected


def test_multicolor_safe_square_stacking() -> None:
    occupancy = OuterPathOccupancy(
        global_index=0,
        pieces=(
            outer_piece("red-1", PlayerColor.RED, 0),
            outer_piece("green-1", PlayerColor.GREEN, 0),
        ),
    )

    outcome = CollisionResolver().resolve(moving_to(0, PlayerColor.YELLOW), occupancy)

    assert outcome.captured_piece is None
    assert len(outcome.destination_occupancy.pieces) == 3
    assert outcome.destination_protected


def test_multiple_same_color_pieces_on_safe_square() -> None:
    occupancy = OuterPathOccupancy(
        global_index=0,
        pieces=(outer_piece("red-1", PlayerColor.RED, 0), outer_piece("red-2", PlayerColor.RED, 0)),
    )

    outcome = CollisionResolver().resolve(moving_to(0), occupancy)

    assert outcome.captured_piece is None
    assert len(outcome.destination_occupancy.pieces) == 3


@pytest.mark.parametrize("destination_kind", ["home", "finished"])
def test_home_path_and_finished_do_not_use_outer_capture_rules(destination_kind: str) -> None:
    piece = Piece(id="red-1", owner_color=PlayerColor.RED)
    proposal = MovementRules().propose_move(piece, 6)
    assert proposal is not None
    if destination_kind == "home":
        final_destination = MoveDestination.home(HomePathPosition(PlayerColor.RED, 0))
    else:
        final_destination = MoveDestination.finished(PlayerColor.RED)

    outcome = CollisionResolver().resolve(replace(proposal, destination=final_destination))

    assert outcome.destination_occupancy is None
    assert outcome.captured_piece is None
