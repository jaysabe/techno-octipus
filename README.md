# techno-octipus

Mechatronics practice and source code for the robotic arm project.

## Overview

MicroPython firmware for an ESP32 that controls a **5-axis robotic arm**
through a Hardware Abstraction Layer (HAL).

```
main.py                 ← Live control loop (runs on boot)
arm/
  config.py             ← Pin assignments, servo limits, PWM settings
  arm_controller.py     ← 5-axis RoboticArm class
  hal/
    pwm_hal.py          ← Low-level PWM HAL (wraps machine.PWM)
    servo_hal.py        ← Servo HAL (angle → pulse width → duty cycle)
tests/
  conftest.py           ← Shared pytest setup (path + machine mock)
  mock_machine.py       ← CPython mock of machine.Pin / machine.PWM
  test_pwm_hal.py       ← Unit tests for PWMChannel
  test_servo_hal.py     ← Unit tests for ServoHAL
  test_arm.py           ← Unit tests for RoboticArm
```

## Architecture

```
main.py  →  RoboticArm  →  ServoHAL ×5  →  PWMChannel  →  machine.PWM
```

Each layer has a single responsibility: `RoboticArm` manages joints,
`ServoHAL` converts degrees to pulse widths, and `PWMChannel` writes duty
cycles to the ESP32 hardware.  Motion commands are fed in through the
`_read_command` stub in `main.py` (UART, Wi-Fi, BLE, etc.).

> **Firmware:** MicroPython ≥ 1.15 (ESP-IDF build). Older builds using
> `PWM.duty()` (0–1023) are handled automatically via runtime detection.

## Hardware wiring (default)

| Servo       | Joint | ESP32 GPIO |
|-------------|-------|------------|
| Base        | 0     | 13         |
| Shoulder    | 1     | 12         |
| Elbow       | 2     | 14         |
| Wrist pitch | 3     | 27         |
| Wrist roll  | 4     | 26         |

Pin assignments and travel limits can be changed in `arm/config.py`.

## Requirements

- ESP32 board running **MicroPython ≥ 1.15** (ESP-IDF based build).
- Standard hobby servos (50 Hz, 500–2500 µs pulse range).

## Flashing to ESP32

Use [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html)
or [ampy](https://github.com/scientifichackers/ampy) to upload the files:

```bash
# Upload the arm package and main loop
mpremote connect /dev/ttyUSB0 cp -r arm/ :
mpremote connect /dev/ttyUSB0 cp main.py :main.py
```

The device will run `main.py` automatically on the next reset.

## Running the demo

After flashing, the base joint sweeps continuously between 0° and 180°.
Connect via the REPL and press **Ctrl-C** to stop; all joints return to
the home position (90°) before the PWM hardware is released.

To send motion commands from your own code, replace the `_read_command`
stub in `main.py` with a UART/Wi-Fi/BLE receive function that returns
`(joint_index, angle_degrees)` tuples.

## Running tests (CPython)

No ESP32 hardware is needed — the `machine` module is mocked automatically:

```bash
pip install pytest
pytest tests/ -v
```
=======
Mechatronics practice and source code for an ESP32-powered robotic arm project,
written in **MicroPython**.

---

## Project structure

```
src/
  main.py    – entry point; runs the live loop and persists the action log
  arm.py     – servo / motor helpers (Joint + Arm classes)
  logger.py  – action-sequence logger (ActionLogger)
```

---

## Hardware

| Joint    | GPIO |
|----------|------|
| Base     | 13   |
| Shoulder | 12   |
| Elbow    | 14   |
| Gripper  | 27   |
| Stop btn | 0 (BOOT button) |

Adjust the `PIN_*` constants in `src/arm.py` and `STOP_PIN` in `src/main.py`
to match your wiring.

---

## Flashing to the ESP32

1. Install MicroPython firmware on your board:
   <https://micropython.org/download/ESP32_GENERIC/>

2. Install `mpremote`:
   ```bash
   pip install mpremote
   ```

3. Copy source files to the board:
   ```bash
   mpremote cp src/logger.py src/arm.py src/main.py :
   ```

4. Run:
   ```bash
   mpremote run src/main.py
   # or reboot the board – MicroPython auto-runs main.py
   ```

---

## Action logger

`ActionLogger` (in `src/logger.py`) records every movement made inside the
live loop with a millisecond timestamp relative to session start.

| Method | Description |
|--------|-------------|
| `log.record(action, **params)` | Append one entry to the in-memory sequence |
| `log.dump()` | Pretty-print the sequence to the REPL |
| `log.save()` | Append the session to `/action_log.txt` on flash |
| `log.clear()` | Reset in-memory log (file untouched) |
| `log.entries` | Read-only list of recorded entries |

Example log output (`log.dump()`):
```
=== Action Log (7 entries) ===
[   0] +     0 ms  home  {}
[   1] +   312 ms  move_base  angle=45
[   2] +   625 ms  move_shoulder  angle=70
...