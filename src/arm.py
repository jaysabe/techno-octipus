# arm.py – Servo / motor helpers for a multi-joint robotic arm on ESP32
#
# Each joint is driven by a PWM signal on an output pin.
# Servo pulse range: 500 µs (0°) – 2500 µs (180°)  @ 50 Hz
#
# Wiring assumption (adjust PIN_* constants to match your board):
#   BASE    → GPIO 13
#   SHOULDER → GPIO 12
#   ELBOW   → GPIO 14
#   GRIPPER → GPIO 27

from machine import Pin, PWM
import utime

# ---------------------------------------------------------------------------
# Pin assignments – update these to match your physical wiring
# ---------------------------------------------------------------------------
PIN_BASE      = 13
PIN_SHOULDER  = 12
PIN_ELBOW     = 14
PIN_GRIPPER   = 27

PWM_FREQ      = 50          # Hz  (standard servo frequency)
DUTY_MIN      = 40          # ~500 µs  → 0°   (1024-step duty cycle)
DUTY_MAX      = 115         # ~2500 µs → 180° (1024-step duty cycle)
MOVE_DELAY_MS = 300         # ms to wait after each move so the servo settles


# ---------------------------------------------------------------------------
# Joint class
# ---------------------------------------------------------------------------

class Joint:
    """A single servo-driven arm joint."""

    def __init__(self, name: str, pin: int):
        self.name = name
        self._pwm = PWM(Pin(pin), freq=PWM_FREQ)
        self._angle = 90        # assume neutral on startup
        self.move(self._angle)  # drive to neutral

    # ------------------------------------------------------------------

    def move(self, angle: int):
        """Move to *angle* degrees (0–180).  Clamps out-of-range values."""
        angle = max(0, min(180, int(angle)))
        duty = DUTY_MIN + int((DUTY_MAX - DUTY_MIN) * angle / 180)
        self._pwm.duty(duty)
        self._angle = angle
        utime.sleep_ms(MOVE_DELAY_MS)

    def off(self):
        """De-energise the servo (prevents holding-current heat)."""
        self._pwm.duty(0)

    @property
    def angle(self) -> int:
        return self._angle

    def __repr__(self):
        return "Joint({}, {}°)".format(self.name, self._angle)


# ---------------------------------------------------------------------------
# Arm class – groups all joints and exposes high-level moves
# ---------------------------------------------------------------------------

class Arm:
    """Four-joint robotic arm controller."""

    def __init__(self):
        self.base     = Joint("base",     PIN_BASE)
        self.shoulder = Joint("shoulder", PIN_SHOULDER)
        self.elbow    = Joint("elbow",    PIN_ELBOW)
        self.gripper  = Joint("gripper",  PIN_GRIPPER)

    # ------------------------------------------------------------------
    # Low-level joint moves
    # ------------------------------------------------------------------

    def move_base(self, angle: int):
        self.base.move(angle)

    def move_shoulder(self, angle: int):
        self.shoulder.move(angle)

    def move_elbow(self, angle: int):
        self.elbow.move(angle)

    def open_gripper(self):
        self.gripper.move(180)

    def close_gripper(self):
        self.gripper.move(0)

    # ------------------------------------------------------------------
    # High-level sequences
    # ------------------------------------------------------------------

    def home(self):
        """Return all joints to the neutral 90° position."""
        for joint in (self.base, self.shoulder, self.elbow, self.gripper):
            joint.move(90)

    def pick(self, base_angle: int = 90):
        """Simple pick routine: rotate, lower, close, raise."""
        self.move_base(base_angle)
        self.move_shoulder(60)
        self.move_elbow(120)
        self.close_gripper()
        self.move_shoulder(90)
        self.move_elbow(90)

    def place(self, base_angle: int = 90):
        """Simple place routine: rotate, lower, open, raise."""
        self.move_base(base_angle)
        self.move_shoulder(60)
        self.move_elbow(120)
        self.open_gripper()
        self.move_shoulder(90)
        self.move_elbow(90)

    def release_all(self):
        """De-energise every servo (call before deep-sleep / shutdown)."""
        for joint in (self.base, self.shoulder, self.elbow, self.gripper):
            joint.off()

    def __repr__(self):
        return "Arm(base={}, shoulder={}, elbow={}, gripper={})".format(
            self.base.angle, self.shoulder.angle,
            self.elbow.angle, self.gripper.angle,
        )
