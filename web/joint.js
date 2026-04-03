/**
 * joint.js
 *
 * Browser-friendly `Joint` class that mirrors the Python `Joint` in src/arm.py.
 *
 * Instead of blocking hardware PWM calls the class uses requestAnimationFrame
 * to smoothly interpolate the joint angle from its current position to a target
 * position over a configurable duration.  `move()` returns a Promise that
 * resolves once the animation completes, so sequences can be written with
 * straightforward async/await.
 *
 * Usage
 * -----
 *   import { Joint } from './joint.js';
 *
 *   const shoulder = new Joint('shoulder');
 *   shoulder.onUpdate = (angle) => renderArm({ shoulder: angle });
 *
 *   // arm must be running its RAF loop (see RoboticArm.start())
 *   await shoulder.move(60);   // animates to 60° over 300 ms
 */

import { ANGLE_MIN, ANGLE_MAX, MOVE_DURATION_MS } from './arm-config.js';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

/**
 * Smooth ease-in-out curve.
 * @param {number} t  Progress in [0, 1].
 * @returns {number}  Eased progress in [0, 1].
 */
function easeInOut(t) {
  return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
}

// ---------------------------------------------------------------------------
// Joint
// ---------------------------------------------------------------------------

export class Joint {
  /**
   * @param {string} name          Human-readable joint name (e.g. 'shoulder').
   * @param {number} [initialAngle=90]  Starting angle in degrees.
   */
  constructor(name, initialAngle = 90) {
    this.name = name;

    // Initial angle is snapped to an integer to match the firmware's integer
    // degree representation.  During animation _angle holds fractional values
    // for smooth interpolation; it snaps back to an integer when the move ends.
    this._angle       = clamp(Math.round(initialAngle), ANGLE_MIN, ANGLE_MAX);
    this._startAngle  = this._angle;
    this._targetAngle = this._angle;
    this._startTime   = null;   // RAF timestamp when the current move began
    this._duration    = 0;      // ms for the current move
    this._resolveMove = null;   // Promise resolve callback

    /**
     * Called on every animation frame while the joint is moving, and once
     * when the move completes.  Receives the current interpolated angle.
     *
     * @type {((angle: number) => void) | null}
     */
    this.onUpdate = null;
  }

  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  /** Current angle in degrees (may be fractional during animation). */
  get angle() {
    return this._angle;
  }

  /**
   * Animate this joint to `targetAngle` over `duration` milliseconds.
   *
   * The move starts on the next animation frame (driven by the owning
   * `RoboticArm`'s RAF loop).  The returned Promise resolves once the
   * animation finishes.
   *
   * @param {number} targetAngle   Destination angle in degrees (0–180).
   * @param {number} [duration]    Animation duration in ms.
   * @returns {Promise<number>}    Resolves with the final angle.
   */
  move(targetAngle, duration = MOVE_DURATION_MS) {
    targetAngle = clamp(Math.round(targetAngle), ANGLE_MIN, ANGLE_MAX);

    // If already at target, resolve immediately.
    if (targetAngle === Math.round(this._angle) && this._resolveMove === null) {
      return Promise.resolve(this._angle);
    }

    // Cancel any in-progress move by resolving its promise early.
    if (this._resolveMove !== null) {
      const prev = this._resolveMove;
      this._resolveMove = null;
      prev(this._angle);
    }

    this._startAngle  = this._angle;
    this._targetAngle = targetAngle;
    this._startTime   = null;   // will be set on the first tick
    this._duration    = Math.max(1, duration);

    return new Promise((resolve) => {
      this._resolveMove = resolve;
    });
  }

  // ---------------------------------------------------------------------------
  // Internal – called by RoboticArm on every animation frame
  // ---------------------------------------------------------------------------

  /**
   * Advance the animation by one frame.
   *
   * @param {DOMHighResTimeStamp} timestamp  Value from requestAnimationFrame.
   */
  _tick(timestamp) {
    if (this._resolveMove === null) return;

    if (this._startTime === null) {
      this._startTime = timestamp;
    }

    const elapsed  = timestamp - this._startTime;
    const progress = Math.min(elapsed / this._duration, 1);
    const eased    = easeInOut(progress);

    this._angle = this._startAngle + (this._targetAngle - this._startAngle) * eased;

    if (this.onUpdate) this.onUpdate(this._angle);

    if (progress >= 1) {
      this._angle     = this._targetAngle;
      this._startTime = null;

      const resolve     = this._resolveMove;
      this._resolveMove = null;
      resolve(this._angle);
    }
  }

  toString() {
    return `Joint(${this.name}, ${Math.round(this._angle)}°)`;
  }
}
