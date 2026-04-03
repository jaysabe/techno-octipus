"""High-level servo abstraction.

Wraps :class:`ServoHAL` and adds a named-limit interface so the rest of
the application only works in physical degrees.
"""

from .hal.servo_hal import ServoHAL


class Servo:
    """Single servo joint with configurable travel limits.

    Args:
        pin_num:      ESP32 GPIO number for the servo signal.
        min_angle:    Soft minimum angle in degrees (default 0).
        max_angle:    Soft maximum angle in degrees (default 180).
        min_pulse_us: PWM pulse width at *min_angle* in µs (default 500).
        max_pulse_us: PWM pulse width at *max_angle* in µs (default 2500).
        freq:         PWM carrier frequency in Hz (default 50).
    """

    def __init__(
        self,
        pin_num: int,
        min_angle: float = 0.0,
        max_angle: float = 180.0,
        min_pulse_us: int = 500,
        max_pulse_us: int = 2500,
        freq: int = 50,
    ) -> None:
        self._hal = ServoHAL(
            pin_num,
            freq=freq,
            min_pulse_us=min_pulse_us,
            max_pulse_us=max_pulse_us,
            min_angle=min_angle,
            max_angle=max_angle,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def move_to(self, angle: float) -> None:
        """Command the servo to move to *angle* degrees.

        Args:
            angle: Target angle in degrees (clamped to configured limits).
        """
        self._hal.write_angle(angle)

    @property
    def angle(self) -> float | None:
        """Current commanded angle in degrees, or ``None`` if not yet set."""
        return self._hal.current_angle

    def deinit(self) -> None:
        """Release underlying hardware resources."""
        self._hal.deinit()
