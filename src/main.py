# main.py – Entry point for the techno-octipus ESP32 arm controller

import utime
from machine import Pin

from arm import Arm
from logger import ActionLogger

STOP_PIN      = 0           # GPIO0 = BOOT button on most DevKit boards
LOOP_DELAY_MS = 100         # ms between live-loop iterations


def live_loop(arm: Arm, log: ActionLogger):
    """Repeating arm movement sequence; logs every action."""
    stop_btn = Pin(STOP_PIN, Pin.IN, Pin.PULL_UP)

    print("[main] Live loop started.  Press BOOT button or Ctrl-C to stop.")

    arm.home()
    log.record("home")

    step = 0

    while True:
        if stop_btn.value() == 0:          # button pulled LOW
            print("[main] Stop button pressed – exiting live loop.")
            break

        if step == 0:
            arm.move_base(45)
            log.record("move_base", angle=45)

        elif step == 1:
            arm.move_shoulder(70)
            log.record("move_shoulder", angle=70)

        elif step == 2:
            arm.move_elbow(110)
            log.record("move_elbow", angle=110)

        elif step == 3:
            arm.pick(base_angle=45)
            log.record("pick", base_angle=45)

        elif step == 4:
            arm.place(base_angle=135)
            log.record("place", base_angle=135)

        elif step == 5:
            arm.home()
            log.record("home")

        # Advance through the sequence, looping back to step 0
        step = (step + 1) % 6

        utime.sleep_ms(LOOP_DELAY_MS)


def main():
    arm = Arm()
    log = ActionLogger()

    try:
        live_loop(arm, log)
    except KeyboardInterrupt:
        print("[main] KeyboardInterrupt – exiting live loop.")
    finally:
        # Always de-energise servos and persist the log
        arm.release_all()
        log.dump()
        log.save()
        print("[main] Done.")


main()
