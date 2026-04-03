/**
 * arm-config.js
 *
 * Shared constants that mirror the Python firmware configuration in src/arm.py
 * and src/main.py.  Import these into any module that needs servo limits or
 * default timing values.
 */

/** Minimum allowed joint angle (degrees). */
export const ANGLE_MIN = 0;

/** Maximum allowed joint angle (degrees). */
export const ANGLE_MAX = 180;

/** Neutral resting angle for all joints (degrees). */
export const NEUTRAL_ANGLE = 90;

/**
 * How long (ms) to animate each single joint move.
 * Mirrors MOVE_DELAY_MS in arm.py — the time the physical servo needs to settle.
 */
export const MOVE_DURATION_MS = 300;

/**
 * Delay (ms) between steps in the live demo loop.
 * Mirrors LOOP_DELAY_MS in main.py.
 */
export const LOOP_DELAY_MS = 100;

/** Ordered list of joint names, matching the Arm class properties. */
export const JOINT_NAMES = ['base', 'shoulder', 'elbow', 'gripper'];

/**
 * Key angles used in the predefined sequences (mirrors main.py values).
 */
export const SEQUENCE_ANGLES = {
  PICK_BASE:     45,   // base angle for the pick() call in the demo loop
  PLACE_BASE:   135,   // base angle for the place() call in the demo loop
  SHOULDER_DOWN: 60,   // shoulder angle used while lowering the arm
  ELBOW_DOWN:   120,   // elbow angle used while extending the arm down
  SHOULDER_DEMO: 70,   // shoulder angle for the individual demo step
  ELBOW_DEMO:   110,   // elbow angle for the individual demo step
};
