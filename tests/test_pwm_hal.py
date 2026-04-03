"""Unit tests for the PWM HAL layer.

These tests run on CPython using the mock machine module so no ESP32
hardware is needed.
"""

from tests.mock_machine import MockPWM
from arm.hal.pwm_hal import PWMChannel


class TestPWMChannel:
    """Tests for PWMChannel."""

    def _make_channel(self, pin: int = 13, freq: int = 50) -> PWMChannel:
        return PWMChannel(pin, freq)

    def test_init_creates_pwm_on_correct_pin(self):
        ch = self._make_channel(pin=13)
        assert ch._pwm.pin.num == 13

    def test_init_sets_frequency(self):
        ch = self._make_channel(freq=50)
        assert ch._pwm._freq == 50

    def test_set_pulse_us_full_range_duty_u16(self):
        ch = self._make_channel(freq=50)
        # 50 Hz → period = 20 000 µs
        # 500 µs pulse → duty = 500/20000 * 65535 ≈ 1638
        ch.set_pulse_us(500)
        expected = int(500 / 20_000 * 65535)
        assert ch._pwm._duty_u16_value == expected

    def test_set_pulse_us_2500_us(self):
        ch = self._make_channel(freq=50)
        ch.set_pulse_us(2500)
        expected = int(2500 / 20_000 * 65535)
        assert ch._pwm._duty_u16_value == expected

    def test_set_pulse_us_clamps_below_zero(self):
        ch = self._make_channel(freq=50)
        ch.set_pulse_us(-100)
        assert ch._pwm._duty_u16_value == 0

    def test_set_pulse_us_clamps_above_period(self):
        ch = self._make_channel(freq=50)
        # Period = 20 000 µs; pass something larger
        ch.set_pulse_us(25_000)
        assert ch._pwm._duty_u16_value == 65535

    def test_set_freq_updates_pwm(self):
        ch = self._make_channel(freq=50)
        ch.set_freq(100)
        assert ch._pwm._freq == 100
        assert ch._freq == 100

    def test_deinit_calls_pwm_deinit(self):
        ch = self._make_channel()
        ch.deinit()
        assert ch._pwm._deinitialized is True

    def test_duty_u16_api_detection(self):
        ch = self._make_channel()
        # MockPWM has duty_u16, so _max_duty must be 65535
        assert ch._max_duty == 65535
        assert ch._duty_fn == ch._pwm.duty_u16

    def test_legacy_duty_fallback(self, monkeypatch):
        """When duty_u16 is absent the channel falls back to duty(0-1023)."""
        import arm.hal.pwm_hal as pwm_hal_module

        class LegacyPWM:
            """PWM stub without duty_u16, matching older MicroPython firmware."""

            def __init__(self, pin, freq: int = 50) -> None:
                self.pin = pin
                self._freq = freq
                self._duty_value: int | None = None
                self._deinitialized = False

            def freq(self, value=None):
                if value is None:
                    return self._freq
                self._freq = value

            def duty(self, value=None):
                if value is None:
                    return self._duty_value
                self._duty_value = value

            def deinit(self) -> None:
                self._deinitialized = True

        # Patch the PWM name inside the already-imported pwm_hal module so
        # the next PWMChannel() call picks up LegacyPWM instead of MockPWM.
        monkeypatch.setattr(pwm_hal_module, "PWM", LegacyPWM)
        ch = PWMChannel(13, 50)
        assert ch._max_duty == 1023
        assert ch._duty_fn == ch._pwm.duty
