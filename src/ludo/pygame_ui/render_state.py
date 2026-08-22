"""Prepare gameplay HUD render state from facade snapshots and board geometry."""

from __future__ import annotations

from collections import Counter, defaultdict

from ludo.app import GameSnapshot, PieceSnapshot, PlayerSnapshot
from ludo.domain.pieces import PieceState
from ludo.domain.players import PIECES_PER_PLAYER
from ludo.domain.turns import TurnPhase
from ludo.geometry import BoardGeometry, ScreenRect
from ludo.pygame_ui import theme
from ludo.pygame_ui.render_models import (
    DiceHudState,
    GameplayRenderState,
    PieceLocationKey,
    PieceLocationKind,
    PieceRenderGroup,
    PieceRenderItem,
    PlayerHudState,
)


def build_gameplay_render_state(
    snapshot: GameSnapshot, geometry: BoardGeometry
) -> GameplayRenderState:
    """Build draw-ready piece, dice, and player HUD state."""
    groups = _piece_groups(snapshot, geometry)
    return GameplayRenderState(
        pieces=groups,
        dice=_dice_state(snapshot, geometry),
        players=tuple(_player_hud(player, snapshot, geometry) for player in snapshot.players),
    )


def _piece_groups(snapshot: GameSnapshot, geometry: BoardGeometry) -> tuple[PieceRenderGroup, ...]:
    grouped: dict[PieceLocationKey, list[PieceRenderItem]] = defaultdict(list)
    bounds_by_location: dict[PieceLocationKey, ScreenRect] = {}
    for player in snapshot.players:
        for yard_slot, piece in enumerate(player.pieces):
            location, bounds = _piece_location(piece, yard_slot, geometry)
            grouped[location].append(
                PieceRenderItem(
                    piece_id=piece.id,
                    symbol=_piece_symbol(piece),
                    color_value=piece.owner_color.value,
                    location=location,
                )
            )
            bounds_by_location[location] = bounds

    return tuple(
        PieceRenderGroup(
            center=bounds_by_location[location].center,
            bounds=bounds_by_location[location],
            pieces=tuple(pieces),
            placeholder_label=_placeholder_label(pieces) if len(pieces) > 1 else None,
        )
        for location, pieces in grouped.items()
    )


def _piece_location(
    piece: PieceSnapshot, yard_slot: int, geometry: BoardGeometry
) -> tuple[PieceLocationKey, ScreenRect]:
    if piece.state is PieceState.IN_YARD:
        center = geometry.yard_piece_positions(piece.owner_color)[yard_slot]
        return (
            PieceLocationKey(PieceLocationKind.YARD, piece.owner_color.value, yard_slot),
            _piece_bounds(center, geometry.cell_size),
        )
    if piece.state is PieceState.ON_OUTER_PATH and piece.path_progress is not None:
        outer_index = geometry.topology.global_outer_index(piece.owner_color, piece.path_progress)
        return (
            PieceLocationKey(PieceLocationKind.OUTER, piece.owner_color.value, outer_index),
            geometry.outer_square(outer_index),
        )
    if piece.state is PieceState.ON_HOME_PATH and piece.path_progress is not None:
        return (
            PieceLocationKey(PieceLocationKind.HOME, piece.owner_color.value, piece.path_progress),
            geometry.home_path_square(piece.owner_color, piece.path_progress),
        )
    return (
        PieceLocationKey(PieceLocationKind.FINISH, piece.owner_color.value),
        geometry.finish_region(piece.owner_color),
    )


def _dice_state(snapshot: GameSnapshot, geometry: BoardGeometry) -> DiceHudState:
    current_color = snapshot.current_player.color.value if snapshot.current_player else ""
    return DiceHudState(
        bounds=geometry.center_dice_area,
        current_value=snapshot.current_dice_value,
        roll_available=(
            snapshot.phase is TurnPhase.WAITING_FOR_ROLL and snapshot.current_player is not None
        ),
        accent_color=theme.color_for_name(current_color),
    )


def _player_hud(
    player: PlayerSnapshot, snapshot: GameSnapshot, geometry: BoardGeometry
) -> PlayerHudState:
    active = snapshot.current_player is not None and snapshot.current_player.id == player.id
    finished_count = sum(piece.state is PieceState.FINISHED for piece in player.pieces)
    status = (
        f"Rank {player.rank}"
        if player.rank is not None
        else f"{finished_count} / {PIECES_PER_PLAYER} finished"
    )
    timeout = max(1, snapshot.decision_timeout_seconds)
    seconds = snapshot.seconds_remaining if active else None
    progress = min(1, max(0, snapshot.seconds_remaining / timeout)) if active else 0
    return PlayerHudState(
        player_id=player.id,
        name=player.name,
        color_value=player.color.value,
        status_text=status,
        active=active,
        label_area=geometry.player_label_area(player.color),
        timer_area=geometry.timer_area(player.color),
        seconds_remaining=seconds,
        timer_progress=progress,
    )


def _placeholder_label(pieces: list[PieceRenderItem]) -> str:
    counts = Counter(piece.symbol for piece in pieces)
    return " ".join(f"{count}{symbol}" for symbol, count in sorted(counts.items()))


def _piece_bounds(center: tuple[int, int], cell_size: int) -> ScreenRect:
    size = int(cell_size * 0.72)
    return ScreenRect(center[0] - size // 2, center[1] - size // 2, size, size)


def _piece_symbol(piece: PieceSnapshot) -> str:
    return piece.owner_color.piece_symbol
