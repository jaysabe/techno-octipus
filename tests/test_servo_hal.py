"""Unit tests for the Servo HAL layer."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import tests.mock_machine  # noqa: F401, E402

import pytest
from arm.hal.servo_hal import ServoHAL


def _make_hal(**kwargs) -> ServoHAL:
    defaults = dict(
        pin_num=13,
        freq=50,
        min_pulse_us=500,
        max_pulse_us=2500,
        min_angle=0.0,
        max_angle=180.0,
    )
    defaults.update(kwargs)
    return ServoHAL(**defaults)


class TestServoHAL:
    def test_current_angle_none_before_write(self):
        hal = _make_hal()
        assert hal.current_angle is None

    def test_write_angle_sets_current_angle(self):
        hal = _make_hal()
        hal.write_angle(90.0)
        assert hal.current_angle == 90.0

    def test_write_angle_clamps_below_min(self):
        hal = _make_hal(min_angle=15.0, max_angle=165.0)
        hal.write_angle(-10.0)
        assert hal.current_angle == 15.0

    def test_write_angle_clamps_above_max(self):
        hal = _make_hal(min_angle=0.0, max_angle=180.0)
        hal.write_angle(200.0)
        assert hal.current_angle == 180.0

    def test_angle_to_pulse_min(self):
        hal = _make_hal()
        assert hal._angle_to_pulse_us(0.0) == 500

    def test_angle_to_pulse_max(self):
        hal = _make_hal()
        assert hal._angle_to_pulse_us(180.0) == 2500

    def test_angle_to_pulse_midpoint(self):
        hal = _make_hal()
        # 90° → midpoint of 500–2500 = 1500
        assert hal._angle_to_pulse_us(90.0) == 1500

    def test_pulse_written_to_pwm_channel(self):
        hal = _make_hal()
        hal.write_angle(0.0)
        # 500 µs / 20 000 µs * 65535
        expected_duty = int(500 / 20_000 * 65535)
        assert hal._pwm._pwm._duty_u16_value == expected_duty

    def test_invalid_angle_range_raises(self):
        with pytest.raises(ValueError):
            ServoHAL(pin_num=13, min_angle=180.0, max_angle=0.0)

    def test_invalid_pulse_range_raises(self):
        with pytest.raises(ValueError):
            ServoHAL(pin_num=13, min_pulse_us=2500, max_pulse_us=500)

    def test_deinit_propagates(self):
        hal = _make_hal()
        hal.deinit()
        assert hal._pwm._pwm._deinitialized is True
