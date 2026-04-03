/**
 * arm.js
 *
 * Browser-friendly `RoboticArm` class that mirrors the Python `Arm` in
 * src/arm.py.
 *
 * All high-level methods (`home`, `pick`, `place`) are async and resolve only
 * after every joint in the sequence has finished animating, matching the
 * sequential blocking behaviour of the firmware.
 *
 * Quick-start
 * -----------
 *   import { RoboticArm } from './arm.js';
 *
 *   const arm = new RoboticArm();
 *
 *   // Register per-joint update callbacks so your renderer stays in sync.
 *   arm.base.onUpdate     = (a) => draw('base', a);
 *   arm.shoulder.onUpdate = (a) => draw('shoulder', a);
 *   arm.elbow.onUpdate    = (a) => draw('elbow', a);
 *   arm.gripper.onUpdate  = (a) => draw('gripper', a);
 *
 *   arm.start();           // begin the requestAnimationFrame loop
 *
 *   await arm.home();
 *   await arm.pick(45);
 *   await arm.place(135);
 *
 *   arm.stop();            // pause the RAF loop when not needed
 */

import { Joint } from './joint.js';
import { MOVE_DURATION_MS } from './arm-config.js';

export class RoboticArm {
  constructor() {
    /** @type {Joint} */
    this.base     = new Joint('base',     90);
    /** @type {Joint} */
    this.shoulder = new Joint('shoulder', 90);
    /** @type {Joint} */
    this.elbow    = new Joint('elbow',    90);
    /** @type {Joint} */
    this.gripper  = new Joint('gripper',  90);

    this._joints    = [this.base, this.shoulder, this.elbow, this.gripper];
    this._rafId     = null;
    this._animating = false;
  }

  // ---------------------------------------------------------------------------
  // Animation loop
  // ---------------------------------------------------------------------------

  /**
   * Start the requestAnimationFrame loop.
   * Must be called before any `move` / sequence method will animate.
   */
  start() {
    if (this._animating) return;
    this._animating = true;

    const loop = (timestamp) => {
      if (!this._animating) return;
      for (const joint of this._joints) joint._tick(timestamp);
      this._rafId = requestAnimationFrame(loop);
    };

    this._rafId = requestAnimationFrame(loop);
  }

  /**
   * Pause the requestAnimationFrame loop.
   * Any in-progress move Promises will be left pending until `start()` is
   * called again.
   */
  stop() {
    this._animating = false;
    if (this._rafId !== null) {
      cancelAnimationFrame(this._rafId);
      this._rafId = null;
    }
  }

  // ---------------------------------------------------------------------------
  // Low-level joint moves (mirror Python methods)
  // ---------------------------------------------------------------------------

  /** @param {number} angle  @param {number} [duration]  @returns {Promise<number>} */
  move_base(angle, duration = MOVE_DURATION_MS) {
    return this.base.move(angle, duration);
  }

  /** @param {number} angle  @param {number} [duration]  @returns {Promise<number>} */
  move_shoulder(angle, duration = MOVE_DURATION_MS) {
    return this.shoulder.move(angle, duration);
  }

  /** @param {number} angle  @param {number} [duration]  @returns {Promise<number>} */
  move_elbow(angle, duration = MOVE_DURATION_MS) {
    return this.elbow.move(angle, duration);
  }

  /** @param {number} [duration]  @returns {Promise<number>} */
  open_gripper(duration = MOVE_DURATION_MS) {
    return this.gripper.move(180, duration);
  }

  /** @param {number} [duration]  @returns {Promise<number>} */
  close_gripper(duration = MOVE_DURATION_MS) {
    return this.gripper.move(0, duration);
  }

  // ---------------------------------------------------------------------------
  // High-level sequences (mirror Python methods, sequential like the firmware)
  // ---------------------------------------------------------------------------

  /**
   * Return all joints to the neutral 90° position.
   * Mirrors `Arm.home()` in arm.py.
   *
   * @param {number} [duration]
   * @returns {Promise<void>}
   */
  async home(duration = MOVE_DURATION_MS) {
    for (const joint of this._joints) {
      await joint.move(90, duration);
    }
  }

  /**
   * Rotate, lower, close gripper, raise.
   * Mirrors `Arm.pick()` in arm.py.
   *
   * @param {number} [base_angle=90]
   * @param {number} [duration]
   * @returns {Promise<void>}
   */
  async pick(base_angle = 90, duration = MOVE_DURATION_MS) {
    await this.move_base(base_angle, duration);
    await this.move_shoulder(60, duration);
    await this.move_elbow(120, duration);
    await this.close_gripper(duration);
    await this.move_shoulder(90, duration);
    await this.move_elbow(90, duration);
  }

  /**
   * Rotate, lower, open gripper, raise.
   * Mirrors `Arm.place()` in arm.py.
   *
   * @param {number} [base_angle=90]
   * @param {number} [duration]
   * @returns {Promise<void>}
   */
  async place(base_angle = 90, duration = MOVE_DURATION_MS) {
    await this.move_base(base_angle, duration);
    await this.move_shoulder(60, duration);
    await this.move_elbow(120, duration);
    await this.open_gripper(duration);
    await this.move_shoulder(90, duration);
    await this.move_elbow(90, duration);
  }

  // ---------------------------------------------------------------------------
  // Utilities
  // ---------------------------------------------------------------------------

  /**
   * Snapshot of every joint's current angle.
   * @returns {{ base: number, shoulder: number, elbow: number, gripper: number }}
   */
  get state() {
    return {
      base:     this.base.angle,
      shoulder: this.shoulder.angle,
      elbow:    this.elbow.angle,
      gripper:  this.gripper.angle,
    };
  }

  toString() {
    const { base, shoulder, elbow, gripper } = this.state;
    return `RoboticArm(base=${Math.round(base)}°, shoulder=${Math.round(shoulder)}°, elbow=${Math.round(elbow)}°, gripper=${Math.round(gripper)}°)`;
  }
}
