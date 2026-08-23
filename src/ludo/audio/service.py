"""Small audio feedback service with generated placeholder tones."""

from __future__ import annotations

import math
from array import array
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

from ludo.app import FacadeResult, FacadeResultKind
from ludo.config import DEFAULT_AUDIO_SETTINGS, AudioSettings


class AudioEvent(StrEnum):
    """UI/gameplay audio event identifiers."""

    DICE_ROLL = "dice_roll"
    MOVE = "move"
    CAPTURE = "capture"
    FINISH = "finish"
    HAZARD = "hazard"
    RANKING = "ranking"
    UI_CLICK = "ui_click"


class AudioBackend(Protocol):
    """Minimal backend contract used by the audio service."""

    def play_tone(self, frequency_hz: int, duration_ms: int, volume: float) -> None:
        """Play one generated tone."""


@dataclass(slots=True)
class NullAudioBackend:
    """No-op backend used when audio is disabled or unavailable."""

    played: list[AudioEvent] = field(default_factory=list)

    def play_tone(self, frequency_hz: int, duration_ms: int, volume: float) -> None:
        """Ignore generated tones."""


@dataclass(slots=True)
class PygameToneBackend:
    """Pygame mixer backend that creates tiny legal placeholder tones."""

    sample_rate: int = 22_050

    def play_tone(self, frequency_hz: int, duration_ms: int, volume: float) -> None:
        """Generate and play a short sine tone, ignoring unavailable audio devices."""
        try:
            import pygame

            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=1)
            sound = pygame.mixer.Sound(buffer=self._tone_buffer(frequency_hz, duration_ms))
            sound.set_volume(max(0.0, min(1.0, volume)))
            sound.play()
        except pygame.error:
            return

    def _tone_buffer(self, frequency_hz: int, duration_ms: int) -> bytes:
        samples = max(1, self.sample_rate * duration_ms // 1000)
        values = array("h")
        for sample in range(samples):
            angle = 2 * math.pi * frequency_hz * sample / self.sample_rate
            envelope = 1 - sample / samples
            values.append(int(math.sin(angle) * envelope * 12_000))
        return values.tobytes()


@dataclass(slots=True)
class AudioService:
    """Map game/UI events to short generated audio cues."""

    settings: AudioSettings = DEFAULT_AUDIO_SETTINGS
    backend: AudioBackend = field(default_factory=PygameToneBackend)

    def play(self, event: AudioEvent) -> None:
        """Play an audio event if audio is enabled."""
        if not self.settings.enabled or self.settings.master_volume <= 0:
            return
        frequency, duration, channel_volume = _cue(event, self.settings)
        self.backend.play_tone(
            frequency,
            duration,
            self.settings.master_volume * channel_volume,
        )

    def play_result(self, result: FacadeResult) -> None:
        """Play appropriate feedback for a facade result."""
        for event in audio_events_for_result(result):
            self.play(event)


def audio_events_for_result(result: FacadeResult) -> tuple[AudioEvent, ...]:
    """Map a resolved facade result to audio events."""
    if result.kind in {
        FacadeResultKind.DICE_ROLLED,
        FacadeResultKind.BASE_DICE_ROLLED,
        FacadeResultKind.SPECIAL_DICE_ROLLED,
    }:
        return (AudioEvent.DICE_ROLL,)
    if result.kind is not FacadeResultKind.PIECE_MOVED:
        return ()
    events = [AudioEvent.MOVE]
    if result.capture_occurred:
        events.append(AudioEvent.CAPTURE)
    if result.hazard_triggered:
        events.append(AudioEvent.HAZARD)
    if result.piece_finished:
        events.append(AudioEvent.FINISH)
    if result.ranked_players:
        events.append(AudioEvent.RANKING)
    return tuple(events)


def _cue(event: AudioEvent, settings: AudioSettings) -> tuple[int, int, float]:
    gameplay = settings.gameplay_volume
    ui = settings.ui_volume
    return {
        AudioEvent.DICE_ROLL: (440, 90, gameplay),
        AudioEvent.MOVE: (520, 70, gameplay),
        AudioEvent.CAPTURE: (220, 140, gameplay),
        AudioEvent.FINISH: (760, 180, gameplay),
        AudioEvent.HAZARD: (150, 160, gameplay),
        AudioEvent.RANKING: (880, 220, gameplay),
        AudioEvent.UI_CLICK: (640, 50, ui),
    }[event]
