"""Servo hardware abstraction layer.

Translates joint angles (in degrees) into PWM pulse widths and delegates
to :class:`PWMChannel` for the actual hardware write.

Pulse-width ↔ angle mapping (linear interpolation)::

    min_pulse_us  →  min_angle
    max_pulse_us  →  max_angle
"""

from .pwm_hal import PWMChannel


class ServoHAL:
    """Servo HAL: angle → pulse-width → PWM duty cycle.

    Args:
        pin_num:      ESP32 GPIO number connected to the servo signal wire.
        freq:         PWM carrier frequency in Hz (default 50).
        min_pulse_us: Pulse width (µs) corresponding to *min_angle*.
        max_pulse_us: Pulse width (µs) corresponding to *max_angle*.
        min_angle:    Minimum allowed angle in degrees.
        max_angle:    Maximum allowed angle in degrees.
    """

    def __init__(
        self,
        pin_num: int,
        freq: int = 50,
        min_pulse_us: int = 500,
        max_pulse_us: int = 2500,
        min_angle: float = 0.0,
        max_angle: float = 180.0,
    ) -> None:
        if min_angle >= max_angle:
            raise ValueError("min_angle must be less than max_angle")
        if min_pulse_us >= max_pulse_us:
            raise ValueError("min_pulse_us must be less than max_pulse_us")

        self._pwm = PWMChannel(pin_num, freq)
        self._min_pulse_us = min_pulse_us
        self._max_pulse_us = max_pulse_us
        self._min_angle = min_angle
        self._max_angle = max_angle
        self._current_angle: float | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def write_angle(self, angle: float) -> None:
        """Move servo to *angle* degrees (clamped to configured limits).

        Args:
            angle: Target angle in degrees.
        """
        angle = max(self._min_angle, min(self._max_angle, float(angle)))
        pulse_us = self._angle_to_pulse_us(angle)
        self._pwm.set_pulse_us(pulse_us)
        self._current_angle = angle

    @property
    def current_angle(self) -> float | None:
        """Last angle written to this servo, or ``None`` if never written."""
        return self._current_angle

    def deinit(self) -> None:
        """Release underlying PWM resource."""
        self._pwm.deinit()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _angle_to_pulse_us(self, angle: float) -> int:
        """Convert *angle* to a pulse width in microseconds."""
        angle_span = self._max_angle - self._min_angle
        pulse_span = self._max_pulse_us - self._min_pulse_us
        pulse_us = self._min_pulse_us + int(
            (angle - self._min_angle) / angle_span * pulse_span
        )
        return pulse_us
