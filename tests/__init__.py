"""Test package for the robotic arm firmware.

Tests run on a standard CPython interpreter by injecting a mock
``machine`` module that simulates the ESP32 ``machine.PWM`` and
``machine.Pin`` APIs.  No physical hardware is required.
"""
