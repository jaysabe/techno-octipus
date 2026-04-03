# techno-octipus
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
================================
```

The on-flash file (`/action_log.txt`) is appended every session so you can
review the full history of movements after the board is powered off.

---

## Live loop

`live_loop()` in `src/main.py` runs until:
- The **BOOT button** (GPIO 0) is pressed, **or**
- A `KeyboardInterrupt` (Ctrl-C) is sent from the REPL.

On exit the arm servos are de-energised, the sequence is printed, and the
log is saved to flash automatically.
