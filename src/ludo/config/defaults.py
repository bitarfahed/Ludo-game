"""Application tuning defaults for presentation systems."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnimationSettings:
    """Tunable animation durations in milliseconds."""

    movement_step_ms: int = 120
    capture_feedback_ms: int = 220
    capture_return_ms: int = 300
    finish_pulse_ms: int = 320
    dice_roll_ms: int = 450
    no_legal_notice_ms: int = 5_000
    feedback_notice_ms: int = 2_000


@dataclass(frozen=True, slots=True)
class AudioSettings:
    """Tunable audio settings."""

    enabled: bool = True
    master_volume: float = 0.35
    ui_volume: float = 0.25
    gameplay_volume: float = 0.35


DEFAULT_ANIMATION_SETTINGS = AnimationSettings()
DEFAULT_AUDIO_SETTINGS = AudioSettings()
