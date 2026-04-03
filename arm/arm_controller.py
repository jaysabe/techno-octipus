"""5-axis robotic arm controller.

Instantiates one :class:`Servo` per axis using the pin assignments and
limits defined in :mod:`arm.config`, and exposes a clean joint-level API
for the live control loop.
"""

from . import config
from .servo import Servo


class RoboticArm:
    """Controller for a 5-axis robotic arm.

    Joint indices and names mirror ``config.JOINT_NAMES``::

        0  base
        1  shoulder
        2  elbow
        3  wrist_pitch
        4  wrist_roll
    """

    # Symbolic joint indices for readability in application code
    JOINT_BASE = 0
    JOINT_SHOULDER = 1
    JOINT_ELBOW = 2
    JOINT_WRIST_PITCH = 3
    JOINT_WRIST_ROLL = 4

    NUM_JOINTS = 5

    def __init__(self) -> None:
        self._servos: list[Servo] = []
        for i, pin in enumerate(config.SERVO_PINS):
            min_a, max_a = config.SERVO_LIMITS[i]
            self._servos.append(
                Servo(
                    pin_num=pin,
                    min_angle=min_a,
                    max_angle=max_a,
                    min_pulse_us=config.SERVO_MIN_PULSE_US,
                    max_pulse_us=config.SERVO_MAX_PULSE_US,
                    freq=config.SERVO_PWM_FREQ,
                )
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def home(self) -> None:
        """Move all joints to the home (neutral) position."""
        for i, angle in enumerate(config.SERVO_HOME):
            self._servos[i].move_to(angle)

    def move_joint(self, joint: int, angle: float) -> None:
        """Move a single joint to *angle* degrees.

        Args:
            joint: Joint index (0–4 or use the ``JOINT_*`` constants).
            angle: Target angle in degrees.

        Raises:
            IndexError: If *joint* is outside [0, NUM_JOINTS).
        """
        if not (0 <= joint < self.NUM_JOINTS):
            raise IndexError(
                f"joint index {joint} out of range [0, {self.NUM_JOINTS})"
            )
        self._servos[joint].move_to(angle)

    def move_all(self, angles: list) -> None:
        """Move all joints simultaneously.

        Extra values in *angles* are ignored; missing values leave the
        corresponding joint unchanged.

        Args:
            angles: Iterable of target angles, one per joint.
        """
        for i, angle in enumerate(angles):
            if i < self.NUM_JOINTS:
                self._servos[i].move_to(angle)

    def get_angles(self) -> list:
        """Return the current commanded angle for every joint.

        Returns:
            List of angles in degrees (``None`` for joints not yet moved).
        """
        return [s.angle for s in self._servos]

    def deinit(self) -> None:
        """Release all PWM hardware resources."""
        for servo in self._servos:
            servo.deinit()
