"""Tests for audio event mapping and muted playback."""

from dataclasses import replace

from ludo.app import FacadeResult, FacadeResultKind, GameSnapshot, PieceSnapshot
from ludo.audio import AudioEvent, AudioService, audio_events_for_result
from ludo.config import AudioSettings
from ludo.domain import PieceState, PlayerColor, TurnPhase


class FakeBackend:
    """Capture generated tones without playing audio."""

    def __init__(self) -> None:
        self.calls: list[tuple[int, int, float]] = []

    def play_tone(self, frequency_hz: int, duration_ms: int, volume: float) -> None:
        self.calls.append((frequency_hz, duration_ms, volume))


def snapshot() -> GameSnapshot:
    return GameSnapshot(
        players=(),
        inactive_colors=frozenset(PlayerColor),
        current_player=None,
        phase=TurnPhase.WAITING_FOR_ROLL,
        seconds_remaining=10,
        decision_timeout_seconds=10,
        current_dice_value=None,
        legal_moves=(),
        outer_occupancies=(),
        rankings=(),
        is_complete=False,
    )


def test_audio_event_mapping_for_facade_results() -> None:
    dice = FacadeResult(FacadeResultKind.DICE_ROLLED, snapshot(), dice_value=6)
    moved = PieceSnapshot("red-1", PlayerColor.RED, PieceState.FINISHED, None)
    captured = PieceSnapshot("blue-1", PlayerColor.BLUE, PieceState.IN_YARD, None)
    move = FacadeResult(
        FacadeResultKind.PIECE_MOVED,
        snapshot(),
        moved_piece=moved,
        captured_piece=captured,
        ranked_players=(),
    )

    assert audio_events_for_result(dice) == (AudioEvent.DICE_ROLL,)
    assert audio_events_for_result(move) == (
        AudioEvent.MOVE,
        AudioEvent.CAPTURE,
        AudioEvent.FINISH,
    )


def test_audio_event_mapping_for_boost_and_shield_results() -> None:
    result = FacadeResult(
        FacadeResultKind.PIECE_MOVED,
        snapshot(),
        boost_triggered=True,
        shield_acquired=True,
        shield_broken=True,
    )

    assert audio_events_for_result(result) == (
        AudioEvent.MOVE,
        AudioEvent.BOOST,
        AudioEvent.SHIELD,
        AudioEvent.SHIELD_BREAK,
    )


def test_muted_audio_does_not_play_or_affect_gameplay_state() -> None:
    backend = FakeBackend()
    settings = replace(AudioSettings(), enabled=False)
    service = AudioService(settings=settings, backend=backend)

    service.play(AudioEvent.MOVE)

    assert backend.calls == []


def test_enabled_audio_routes_to_backend_with_volume() -> None:
    backend = FakeBackend()
    service = AudioService(
        settings=AudioSettings(master_volume=0.5, gameplay_volume=0.4),
        backend=backend,
    )

    service.play(AudioEvent.DICE_ROLL)

    assert len(backend.calls) == 1
    assert backend.calls[0][2] == 0.2
