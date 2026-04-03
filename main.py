"""ESP32 live loop – entry point for the 5-axis robotic arm."""

import time

from arm import config
from arm.arm_controller import RoboticArm


# ---------------------------------------------------------------------------
# Optional: plug in your own command source here
# ---------------------------------------------------------------------------

def _read_command(arm: RoboticArm) -> tuple[int, float] | None:
    """Return the next (joint, angle) command, or ``None`` to keep looping.

    Replace this stub with a real source:
    * ``uart.readline()`` for serial control
    * A Wi-Fi/BLE receive buffer
    * A pre-recorded sequence for replay

    The default implementation runs a continuous demo sweep of the base
    joint so the arm visibly moves when first powered on.
    """
    return None  # no external command – demo sweep handles motion


# ---------------------------------------------------------------------------
# Internal demo: sweep base joint back and forth
# ---------------------------------------------------------------------------

def _demo_sweep(arm: RoboticArm) -> None:
    """Single sweep cycle of the base joint (0 → 180 → 0 degrees)."""
    for angle in range(0, 181, 5):
        arm.move_joint(RoboticArm.JOINT_BASE, angle)
        time.sleep_ms(config.LOOP_DELAY_MS)
    for angle in range(180, -1, -5):
        arm.move_joint(RoboticArm.JOINT_BASE, angle)
        time.sleep_ms(config.LOOP_DELAY_MS)


# ---------------------------------------------------------------------------
# Main live loop
# ---------------------------------------------------------------------------

def run() -> None:
    """Initialise the arm and enter the live control loop.

    The loop runs at approximately ``1000 / LOOP_DELAY_MS`` Hz.  Each
    iteration:

    1. Calls ``_read_command`` to check for new motion commands.
    2. Executes the command if one was returned.
    3. Falls back to the demo sweep when no external source is present.

    The loop exits cleanly on ``KeyboardInterrupt`` (Ctrl-C in the REPL),
    returning all joints to home before releasing the PWM hardware.
    """
    print("Initialising robotic arm …")
    arm = RoboticArm()
    arm.home()
    print("Home position set.  Entering live loop (Ctrl-C to stop).")

    try:
        while True:
            cmd = _read_command(arm)
            if cmd is not None:
                joint, angle = cmd
                arm.move_joint(joint, angle)
                time.sleep_ms(config.LOOP_DELAY_MS)
            else:
                _demo_sweep(arm)
    except KeyboardInterrupt:
        print("\nInterrupted – returning to home position.")
        arm.home()
    finally:
        arm.deinit()
        print("PWM resources released.  Goodbye.")


# ---------------------------------------------------------------------------
# Boot entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run()
