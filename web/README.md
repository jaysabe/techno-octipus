# web — JavaScript Animation Modules

These four ES modules extract the key motion logic from the ESP32 firmware
(`src/arm.py`, `src/main.py`) into pure browser-friendly JavaScript so the
same pick-and-place sequence can be replayed as a smooth CSS/Canvas/SVG
animation on a portfolio website.

## Module overview

| File | Purpose |
|------|---------|
| `arm-config.js` | Shared constants — angle limits, timing values, sequence angles |
| `joint.js` | `Joint` class — smooth angle interpolation via `requestAnimationFrame` |
| `arm.js` | `RoboticArm` class — groups four joints, exposes `home / pick / place` |
| `arm-sequence.js` | `runDemoSequence()` — the six-step repeating loop from `main.py` |

## Quick start

```html
<!-- In your portfolio page -->
<script type="module">
  import { RoboticArm }      from './web/arm.js';
  import { runDemoSequence } from './web/arm-sequence.js';

  const arm = new RoboticArm();

  // Wire each joint to your renderer (Canvas, SVG, CSS transforms, etc.)
  arm.base.onUpdate     = (angle) => updateSegment('base',     angle);
  arm.shoulder.onUpdate = (angle) => updateSegment('shoulder', angle);
  arm.elbow.onUpdate    = (angle) => updateSegment('elbow',    angle);
  arm.gripper.onUpdate  = (angle) => updateSegment('gripper',  angle);

  // Start the requestAnimationFrame loop.
  arm.start();

  // Run the demo sequence continuously.
  // Pass an AbortController signal to stop it later.
  const controller = new AbortController();
  runDemoSequence(arm, {
    signal: controller.signal,
    onStep: (name, params) => console.log(name, params),
  });

  // Stop when the user navigates away.
  window.addEventListener('pagehide', () => controller.abort());
</script>
```

## API reference

### `arm-config.js`

```js
ANGLE_MIN          // 0   — minimum joint angle
ANGLE_MAX          // 180 — maximum joint angle
NEUTRAL_ANGLE      // 90  — home position
MOVE_DURATION_MS   // 300 — default animation duration per move (ms)
LOOP_DELAY_MS      // 100 — delay between demo loop steps (ms)
JOINT_NAMES        // ['base', 'shoulder', 'elbow', 'gripper']
SEQUENCE_ANGLES    // { PICK_BASE, PLACE_BASE, SHOULDER_DOWN, … }
```

### `Joint`

```js
const joint = new Joint('shoulder', 90);

joint.onUpdate = (angle) => { /* called every frame during animation */ };

await joint.move(60);          // animate to 60° over MOVE_DURATION_MS
await joint.move(60, 500);     // animate to 60° over 500 ms

joint.angle;                   // current angle (may be fractional mid-animation)
```

`move()` returns a `Promise<number>` that resolves with the final angle once
the animation completes.  Starting a new `move()` while one is in progress
immediately resolves the old promise and starts the new one.

### `RoboticArm`

```js
const arm = new RoboticArm();

arm.start();   // begin the RAF loop (required before any move will animate)
arm.stop();    // pause the RAF loop

// Low-level
await arm.move_base(45);
await arm.move_shoulder(70);
await arm.move_elbow(110);
await arm.open_gripper();
await arm.close_gripper();

// High-level sequences (sequential, mirroring the firmware)
await arm.home();          // all joints → 90°
await arm.pick(45);        // rotate 45° → lower → close gripper → raise
await arm.place(135);      // rotate 135° → lower → open gripper → raise

// Optional duration override (ms) for all of the above
await arm.home(600);
await arm.pick(45, 600);

arm.state;   // { base, shoulder, elbow, gripper } — current angles snapshot
```

### `runDemoSequence(arm, options)`

Runs the six-step sequence from `main.py` in an infinite async loop:

1. `move_base(45)`
2. `move_shoulder(70)`
3. `move_elbow(110)`
4. `pick(45)`
5. `place(135)`
6. `home()`

Options:

| Option | Type | Description |
|--------|------|-------------|
| `signal` | `AbortSignal` | Stop the loop after the current step |
| `onStep` | `(name, params) => void` | Callback before each step (mirrors `log.record()`) |
| `moveDuration` | `number` | Override per-joint animation duration (ms) |

## Correspondence with the firmware

| Python (src/) | JavaScript (web/) |
|---------------|-------------------|
| `arm.py` `MOVE_DELAY_MS` | `arm-config.js` `MOVE_DURATION_MS` ¹ |
| `arm.py` `Joint.move(angle)` | `joint.js` `Joint.move(angle, duration)` |
| `arm.py` `Arm.home()` | `arm.js` `RoboticArm.home()` |
| `arm.py` `Arm.pick(base_angle)` | `arm.js` `RoboticArm.pick(base_angle)` |
| `arm.py` `Arm.place(base_angle)` | `arm.js` `RoboticArm.place(base_angle)` |
| `main.py` live loop | `arm-sequence.js` `runDemoSequence()` |
| `main.py` `LOOP_DELAY_MS` | `arm-config.js` `LOOP_DELAY_MS` |
| `logger.py` `log.record()` | `arm-sequence.js` `onStep` callback |

> ¹ The Python constant is named `MOVE_DELAY_MS` because it represents a
> blocking `sleep` that lets the servo settle.  The JavaScript equivalent is
> named `MOVE_DURATION_MS` because it represents an animation duration — the
> semantic intent is the same (how long a single move takes), but "duration"
> better describes a tween rather than a hardware delay.
