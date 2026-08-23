"""Prepare gameplay HUD render state from facade snapshots and board geometry."""

from __future__ import annotations

from collections import Counter, defaultdict

from ludo.app import GameSnapshot, OuterOccupancySnapshot, PieceSnapshot, PlayerSnapshot
from ludo.domain.pieces import PieceState
from ludo.domain.players import PIECES_PER_PLAYER
from ludo.domain.turns import TurnPhase
from ludo.geometry import BoardGeometry, ScreenRect
from ludo.pygame_ui import theme
from ludo.pygame_ui.render_models import (
    DiceHudState,
    GameplayRenderState,
    OccupancyInspection,
    OccupancyInspectionLine,
    PieceLocationKey,
    PieceLocationKind,
    PieceRenderGroup,
    PieceRenderItem,
    PlayerHudState,
    StackSummaryComponent,
)

COLOR_ORDER = ("red", "green", "yellow", "blue")
POPUP_WIDTH = 150
POPUP_BASE_HEIGHT = 32
POPUP_LINE_HEIGHT = 22


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
    occupancy_by_outer = {
        occupancy.global_index: occupancy for occupancy in snapshot.outer_occupancies
    }
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
            summary_components=_summary_components(pieces) if len(pieces) > 1 else (),
            inspection=_inspection_for(
                pieces,
                bounds_by_location[location],
                geometry,
                _occupancy_for(location, occupancy_by_outer),
            ),
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
            PieceLocationKey(PieceLocationKind.OUTER, "shared", outer_index),
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
        base_bounds=geometry.base_die_area,
        special_bounds=geometry.special_die_area,
        current_value=snapshot.current_dice_value,
        special_bonus=snapshot.current_special_bonus,
        special_bonus_applied=snapshot.special_bonus_applied,
        movement_value=snapshot.approved_movement_value,
        base_roll_available=(
            snapshot.phase is TurnPhase.WAITING_FOR_ROLL and snapshot.current_player is not None
        ),
        special_roll_available=(
            snapshot.phase is TurnPhase.WAITING_FOR_SPECIAL_ROLL
            and snapshot.current_player is not None
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


def build_occupancy_inspection(
    snapshot: GameSnapshot, geometry: BoardGeometry, point: tuple[int, int]
) -> OccupancyInspection | None:
    """Return hover inspection for an occupied square under ``point``."""
    for group in _piece_groups(snapshot, geometry):
        if group.inspection is not None and group.bounds.contains(point):
            return group.inspection
    return None


def _summary_components(pieces: list[PieceRenderItem]) -> tuple[StackSummaryComponent, ...]:
    counts = Counter(piece.color_value for piece in pieces)
    symbol_by_color = {piece.color_value: piece.symbol for piece in pieces}
    return tuple(
        StackSummaryComponent(counts[color_value], symbol_by_color[color_value], color_value)
        for color_value in COLOR_ORDER
        if counts[color_value]
    )


def _inspection_for(
    pieces: list[PieceRenderItem],
    anchor: ScreenRect,
    geometry: BoardGeometry,
    occupancy: OuterOccupancySnapshot | None,
) -> OccupancyInspection | None:
    if not pieces:
        return None
    counts = Counter(piece.color_value for piece in pieces)
    lines = tuple(
        OccupancyInspectionLine(color_value.title(), color_value, counts[color_value])
        for color_value in COLOR_ORDER
        if counts[color_value]
    )
    is_safe = occupancy.is_safe if occupancy is not None else False
    is_protected = (
        occupancy.is_protected and not occupancy.is_safe if occupancy is not None else False
    )
    status_count = int(is_safe) + int(is_protected)
    return OccupancyInspection(
        anchor=anchor,
        popup=_popup_rect(anchor, len(lines) + status_count, geometry.window_size),
        lines=lines,
        is_safe=is_safe,
        is_protected=is_protected,
    )


def _occupancy_for(
    location: PieceLocationKey,
    occupancy_by_outer: dict[int, OuterOccupancySnapshot],
) -> OuterOccupancySnapshot | None:
    if location.kind is PieceLocationKind.OUTER and location.index is not None:
        return occupancy_by_outer.get(location.index)
    return None


def _popup_rect(
    anchor: ScreenRect, line_count: int, window_size: tuple[int, int]
) -> ScreenRect:
    width, height = window_size
    popup_height = POPUP_BASE_HEIGHT + line_count * POPUP_LINE_HEIGHT
    x = anchor.x + anchor.width + 10
    y = anchor.y - 6
    if x + POPUP_WIDTH > width:
        x = anchor.x - POPUP_WIDTH - 10
    if y + popup_height > height:
        y = height - popup_height - 8
    return ScreenRect(max(8, x), max(8, y), POPUP_WIDTH, popup_height)


def _piece_bounds(center: tuple[int, int], cell_size: int) -> ScreenRect:
    size = int(cell_size * 0.72)
    return ScreenRect(center[0] - size // 2, center[1] - size // 2, size, size)


def _piece_symbol(piece: PieceSnapshot) -> str:
    return piece.owner_color.piece_symbol
