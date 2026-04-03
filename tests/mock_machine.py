"""Lightweight mock of the MicroPython ``machine`` module.

Imported automatically by the test suite before any ``arm`` module is
loaded so that the production code's ``from machine import Pin, PWM``
resolves to these stubs instead of the real hardware driver.

The mock records every call so tests can assert on the values that were
written to the (virtual) PWM channels.
"""

import sys
from unittest.mock import MagicMock


class MockPWM:
    """Simulates ``machine.PWM`` for a single GPIO channel."""

    def __init__(self, pin, freq: int = 50) -> None:
        self.pin = pin
        self._freq = freq
        self._duty_u16_value: int | None = None
        self._duty_value: int | None = None
        self._deinitialized = False

    # --- PWM API surface used by PWMChannel ---

    def freq(self, value: int | None = None):
        if value is None:
            return self._freq
        self._freq = value

    def duty_u16(self, value: int | None = None):
        if value is None:
            return self._duty_u16_value
        self._duty_u16_value = value

    def duty(self, value: int | None = None):
        if value is None:
            return self._duty_value
        self._duty_value = value

    def deinit(self) -> None:
        self._deinitialized = True


class MockPin:
    """Simulates ``machine.Pin``."""

    OUT = 1

    def __init__(self, num, mode=None) -> None:
        self.num = num
        self.mode = mode


# ---------------------------------------------------------------------------
# Inject the mock module into sys.modules so ``from machine import …`` works
# ---------------------------------------------------------------------------

_machine_mock = MagicMock()
_machine_mock.Pin = MockPin
_machine_mock.PWM = MockPWM

sys.modules.setdefault("machine", _machine_mock)
