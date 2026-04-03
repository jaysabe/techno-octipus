# techno-octipus

Mechatronics practice and source code for an ESP32-powered robotic arm project,
written in **MicroPython**.

## Project structure

```
main.py                 ← HAL live loop (runs on boot)
arm/
  config.py             ← Pin assignments, servo limits, PWM settings
  arm_controller.py     ← 5-axis RoboticArm class
  hal/
    pwm_hal.py          ← Low-level PWM HAL (wraps machine.PWM)
    servo_hal.py        ← Servo HAL (angle → pulse width → duty cycle)
src/
  main.py               ← Entry point; runs the live loop and persists the action log
  arm.py                ← Servo/motor helpers (Joint + Arm classes)
  logger.py             ← Action-sequence logger (ActionLogger)
tests/
  conftest.py           ← Shared pytest setup (path + machine mock)
  mock_machine.py       ← CPython mock of machine.Pin / machine.PWM
  test_pwm_hal.py       ← Unit tests for PWMChannel
  test_servo_hal.py     ← Unit tests for ServoHAL
  test_arm.py           ← Unit tests for RoboticArm
```

## Architecture

The HAL-based module (`arm/`) uses a layered design:

```
main.py  →  RoboticArm  →  ServoHAL ×5  →  PWMChannel  →  machine.PWM
```

Each layer has a single responsibility: `RoboticArm` manages joints,
`ServoHAL` converts degrees to pulse widths (500–2500 µs @ 50 Hz), and
`PWMChannel` writes duty cycles to the ESP32 hardware. Older MicroPython
builds using `PWM.duty()` (0–1023) are detected and handled automatically.
Motion commands are fed in through the `_read_command` stub in `main.py`
(UART, Wi-Fi, BLE, etc.).

The simpler `src/` module drives joints directly via `PWM.duty()` and adds an
`ActionLogger` that timestamps every movement and persists the session to
`/action_log.txt` on flash. The loop runs until the BOOT button (GPIO 0) is
pressed or a `KeyboardInterrupt` is received.

## Hardware wiring (default)

| Joint       | GPIO | Notes                    |
|-------------|------|--------------------------|
| Base        | 13   |                          |
| Shoulder    | 12   |                          |
| Elbow       | 14   |                          |
| Wrist pitch | 27   | HAL module only          |
| Wrist roll  | 26   | HAL module only          |
| Gripper     | 27   | `src/` module only       |
| Stop button | 0    | BOOT button on DevKit    |

Adjust pin constants in `arm/config.py` (HAL module) or `src/arm.py` (src module).

## Requirements

- ESP32 board running **MicroPython ≥ 1.15** (ESP-IDF based build).
- Standard hobby servos (50 Hz, 500–2500 µs pulse range).

## Flashing to ESP32

Install [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html), then:

```bash
# HAL module
mpremote connect /dev/ttyUSB0 cp -r arm/ :
mpremote connect /dev/ttyUSB0 cp main.py :main.py

# src/ module
mpremote cp src/logger.py src/arm.py src/main.py :
```

The device runs `main.py` automatically on the next reset.

## Action logger

`ActionLogger` (`src/logger.py`) records every movement with a millisecond
timestamp relative to session start.

| Method | Description |
|--------|-------------|
| `log.record(action, **params)` | Append one entry to the in-memory sequence |
| `log.dump()` | Pretty-print the sequence to the REPL |
| `log.save()` | Append the session to `/action_log.txt` on flash |
| `log.clear()` | Reset in-memory log (file untouched) |
| `log.entries` | Read-only list of recorded entries |

## Running tests (CPython)

No ESP32 hardware needed — the `machine` module is mocked automatically:

```bash
pip install pytest
pytest tests/ -v
```