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
  servo.py              ← High-level Servo abstraction
  hal/
    pwm_hal.py          ← Low-level PWM HAL (wraps machine.PWM)
    servo_hal.py        ← Servo HAL (angle → pulse width → duty cycle)
tests/
  mock_machine.py       ← CPython mock of machine.Pin / machine.PWM
  test_pwm_hal.py       ← Unit tests for PWMChannel
  test_servo_hal.py     ← Unit tests for ServoHAL
  test_arm.py           ← Unit tests for Servo and RoboticArm
```

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
