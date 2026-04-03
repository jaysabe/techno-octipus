/**
 * arm-sequence.js
 *
 * Reproduces the repeating six-step demo sequence from src/main.py as an
 * async loop that runs inside the browser.
 *
 * The loop mirrors the exact order and angles used in the firmware:
 *
 *   Step 0 – move_base(45)
 *   Step 1 – move_shoulder(70)
 *   Step 2 – move_elbow(110)
 *   Step 3 – pick(base_angle=45)
 *   Step 4 – place(base_angle=135)
 *   Step 5 – home()
 *   (repeat)
 *
 * Usage
 * -----
 *   import { RoboticArm }    from './arm.js';
 *   import { runDemoSequence } from './arm-sequence.js';
 *
 *   const arm = new RoboticArm();
 *   arm.start();
 *
 *   // Stop the loop by aborting the controller.
 *   const controller = new AbortController();
 *   runDemoSequence(arm, { signal: controller.signal, onStep: console.log });
 *
 *   // Later …
 *   controller.abort();   // sequence stops after the current step completes
 */

import { LOOP_DELAY_MS, SEQUENCE_ANGLES } from './arm-config.js';

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Returns a Promise that resolves after `ms` milliseconds.
 * @param {number} ms
 * @returns {Promise<void>}
 */
function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Run the firmware demo sequence in an infinite async loop.
 *
 * The loop advances one step per iteration, wrapping back to step 0 after
 * step 5 — exactly as the `while True` loop in main.py does.
 *
 * @param {import('./arm.js').RoboticArm} arm
 *   A `RoboticArm` instance whose `start()` method has already been called.
 *
 * @param {object}   [options]
 * @param {AbortSignal} [options.signal]
 *   An `AbortSignal` (from an `AbortController`) that stops the loop after
 *   the current step finishes.  If omitted the loop runs forever.
 * @param {(stepName: string, params: object) => void} [options.onStep]
 *   Optional callback invoked just before each step executes, receiving the
 *   step name and its parameters (mirrors the `log.record()` calls in main.py).
 * @param {number} [options.moveDuration]
 *   Override the per-joint animation duration (ms).  Defaults to the value in
 *   arm-config.js (MOVE_DURATION_MS = 300 ms).
 *
 * @returns {Promise<void>}  Resolves when the loop is stopped via `signal`.
 *   If `signal` is omitted the returned Promise never resolves (the loop runs
 *   indefinitely until the page is unloaded).
 */
export async function runDemoSequence(arm, { signal, onStep, moveDuration } = {}) {
  const dur = moveDuration;   // undefined → each arm method uses its own default

  const steps = [
    {
      name: 'move_base',
      params: { angle: SEQUENCE_ANGLES.PICK_BASE },
      run: () => arm.move_base(SEQUENCE_ANGLES.PICK_BASE, dur),
    },
    {
      name: 'move_shoulder',
      params: { angle: SEQUENCE_ANGLES.SHOULDER_DEMO },
      run: () => arm.move_shoulder(SEQUENCE_ANGLES.SHOULDER_DEMO, dur),
    },
    {
      name: 'move_elbow',
      params: { angle: SEQUENCE_ANGLES.ELBOW_DEMO },
      run: () => arm.move_elbow(SEQUENCE_ANGLES.ELBOW_DEMO, dur),
    },
    {
      name: 'pick',
      params: { base_angle: SEQUENCE_ANGLES.PICK_BASE },
      run: () => arm.pick(SEQUENCE_ANGLES.PICK_BASE, dur),
    },
    {
      name: 'place',
      params: { base_angle: SEQUENCE_ANGLES.PLACE_BASE },
      run: () => arm.place(SEQUENCE_ANGLES.PLACE_BASE, dur),
    },
    {
      name: 'home',
      params: {},
      run: () => arm.home(dur),
    },
  ];

  // Mirror the firmware's initial home() call before entering the loop.
  onStep?.('home', {});
  await arm.home(dur);

  let step = 0;

  while (!signal?.aborted) {
    const { name, params, run } = steps[step];

    onStep?.(name, params);
    await run();

    step = (step + 1) % steps.length;

    // Mirror LOOP_DELAY_MS between iterations.
    if (!signal?.aborted) {
      await delay(LOOP_DELAY_MS);
    }
  }
}
