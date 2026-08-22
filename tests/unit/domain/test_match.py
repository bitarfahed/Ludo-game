"""Unit tests for match setup, ranking, and completion."""

from dataclasses import replace

import pytest

from ludo.domain import FixedClock, FixedDice, Match, Piece, PieceState, PlayerColor, TurnPhase
from ludo.domain.match import FixedColorRandomizer


def finished_piece(piece_id: str, color: PlayerColor) -> Piece:
    return Piece(id=piece_id, owner_color=color, state=PieceState.FINISHED)


def finish_player(match: Match, color: PlayerColor) -> None:
    active_player = match.player_by_color(color)
    pieces = tuple(finished_piece(piece.id, color) for piece in active_player.pieces)
    match.turn_engine.replace_player(replace(active_player, pieces=pieces))


def create_match(player_count: int, assigned_colors: tuple[PlayerColor, ...]) -> Match:
    choices = [assigned_colors] if player_count == 2 else []
    return Match.create(
        player_names=tuple(f"P{index}" for index in range(1, player_count + 1)),
        color_randomizer=FixedColorRandomizer(choices=choices, samples=[assigned_colors]),
        dice=FixedDice([1, 1, 1, 1]),
        clock=FixedClock(),
    )


def test_valid_two_player_setup_uses_opposite_colors_and_clockwise_order() -> None:
    match = Match.create(
        player_names=("Alice", "Bob"),
        color_randomizer=FixedColorRandomizer(
            choices=[(PlayerColor.GREEN, PlayerColor.BLUE)],
            samples=[(PlayerColor.BLUE, PlayerColor.GREEN)],
        ),
        dice=FixedDice([1]),
        clock=FixedClock(),
    )

    assert {player.color for player in match.players} == {PlayerColor.GREEN, PlayerColor.BLUE}
    assert match.inactive_colors == frozenset({PlayerColor.RED, PlayerColor.YELLOW})
    assert [player.color for player in match.players] == [PlayerColor.GREEN, PlayerColor.BLUE]


def test_valid_three_player_setup_has_one_inactive_color() -> None:
    match = create_match(3, (PlayerColor.BLUE, PlayerColor.RED, PlayerColor.YELLOW))

    assert {player.color for player in match.players} == {
        PlayerColor.RED,
        PlayerColor.YELLOW,
        PlayerColor.BLUE,
    }
    assert match.inactive_colors == frozenset({PlayerColor.GREEN})
    assert [player.color for player in match.players] == [
        PlayerColor.RED,
        PlayerColor.YELLOW,
        PlayerColor.BLUE,
    ]


def test_valid_four_player_setup_uses_all_colors() -> None:
    match = create_match(
        4, (PlayerColor.BLUE, PlayerColor.YELLOW, PlayerColor.GREEN, PlayerColor.RED)
    )

    assert {player.color for player in match.players} == set(PlayerColor)
    assert match.inactive_colors == frozenset()


@pytest.mark.parametrize("player_names", [("Solo",), ("P1", "P2", "P3", "P4", "P5")])
def test_invalid_player_counts_are_rejected(player_names: tuple[str, ...]) -> None:
    with pytest.raises(ValueError, match="2, 3, or 4"):
        Match.create(player_names=player_names)


def test_two_player_colors_are_always_opposite() -> None:
    match = Match.create(
        player_names=("Alice", "Bob"),
        color_randomizer=FixedColorRandomizer(
            choices=[(PlayerColor.RED, PlayerColor.YELLOW)],
            samples=[(PlayerColor.YELLOW, PlayerColor.RED)],
        ),
    )

    assert {player.color for player in match.players} == {PlayerColor.RED, PlayerColor.YELLOW}


def test_four_player_colors_are_all_unique() -> None:
    match = create_match(
        4, (PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE)
    )

    assert len({player.color for player in match.players}) == 4


def test_player_completion_requires_all_four_pieces_finished() -> None:
    match = create_match(2, (PlayerColor.RED, PlayerColor.YELLOW))
    red_player = match.player_by_color(PlayerColor.RED)
    nearly_finished = replace(
        red_player,
        pieces=(
            finished_piece("r1", PlayerColor.RED),
            finished_piece("r2", PlayerColor.RED),
            finished_piece("r3", PlayerColor.RED),
            red_player.pieces[3],
        ),
    )
    match.turn_engine.replace_player(nearly_finished)

    match.evaluate_rankings()

    assert match.rankings == ()
    assert not match.is_complete


def test_first_and_subsequent_completed_players_receive_ranks() -> None:
    match = create_match(
        4, (PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE)
    )

    finish_player(match, PlayerColor.GREEN)
    match.evaluate_rankings()
    finish_player(match, PlayerColor.BLUE)
    match.evaluate_rankings()

    assert [(entry.rank, entry.player.color) for entry in match.rankings[:2]] == [
        (1, PlayerColor.GREEN),
        (2, PlayerColor.BLUE),
    ]


def test_ranked_player_is_skipped_in_future_turns() -> None:
    match = create_match(3, (PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW))
    finish_player(match, PlayerColor.RED)

    match.evaluate_rankings()

    assert match.turn_engine.current_player.color is PlayerColor.GREEN
    assert PlayerColor.RED not in {player.color for player in match.turn_engine.players}


def test_player_cannot_receive_multiple_ranks() -> None:
    match = create_match(3, (PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW))
    finish_player(match, PlayerColor.RED)

    match.evaluate_rankings()
    match.evaluate_rankings()

    assert [(entry.rank, entry.player.color) for entry in match.rankings] == [(1, PlayerColor.RED)]


@pytest.mark.parametrize(
    ("player_count", "colors"),
    [
        (2, (PlayerColor.RED, PlayerColor.YELLOW)),
        (3, (PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW)),
        (4, (PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE)),
    ],
)
def test_automatic_final_rank_and_match_completion(
    player_count: int, colors: tuple[PlayerColor, ...]
) -> None:
    match = create_match(player_count, colors)

    for color in colors[:-1]:
        finish_player(match, color)
        match.evaluate_rankings()

    assert match.is_complete
    assert [entry.rank for entry in match.rankings] == list(range(1, player_count + 1))
    assert [entry.player.color for entry in match.final_standings] == list(colors)


def test_turn_engine_can_continue_after_ranked_current_player_removed() -> None:
    match = create_match(3, (PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW))
    finish_player(match, PlayerColor.RED)

    match.evaluate_rankings()

    assert match.turn_engine.phase is TurnPhase.WAITING_FOR_ROLL
    assert match.turn_engine.current_player.color is PlayerColor.GREEN
