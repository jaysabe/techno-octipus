"""Low-level PWM hardware abstraction layer for ESP32 (MicroPython)."""

from machine import Pin, PWM  # noqa: E402  (MicroPython built-in)


class PWMChannel:
    """Single PWM channel with a microsecond pulse-width interface.

    Args:
        pin_num: ESP32 GPIO number to use for PWM output.
        freq:    PWM carrier frequency in Hz (default 50 for servos).
    """

    _PERIOD_US_DIVISOR = 1_000_000  # µs per second

    def __init__(self, pin_num: int, freq: int = 50) -> None:
        self._freq = freq
        self._pwm = PWM(Pin(pin_num, Pin.OUT), freq=freq)

        # Detect which duty API is available at runtime so the class works
        # with both legacy (duty 0-1023) and modern (duty_u16 0-65535)
        # MicroPython builds without compile-time feature flags.
        if hasattr(self._pwm, "duty_u16"):
            self._max_duty = 65535
            self._duty_fn = self._pwm.duty_u16
        else:
            self._max_duty = 1023
            self._duty_fn = self._pwm.duty

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_pulse_us(self, pulse_us: int) -> None:
        """Set output pulse width in microseconds.

        The value is automatically clamped to ``[0, period_us]``.

        Args:
            pulse_us: Desired pulse width in microseconds.
        """
        period_us = self._PERIOD_US_DIVISOR // self._freq
        pulse_us = max(0, min(period_us, pulse_us))
        duty = int(pulse_us / period_us * self._max_duty)
        self._duty_fn(duty)

    def set_freq(self, freq: int) -> None:
        """Change PWM carrier frequency.

        Args:
            freq: New frequency in Hz.
        """
        self._freq = freq
        self._pwm.freq(freq)

    def deinit(self) -> None:
        """Release the underlying PWM hardware resource."""
        self._pwm.deinit()
