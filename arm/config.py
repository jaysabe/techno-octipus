# Servo pin assignments for the 5-axis robotic arm (ESP32 GPIO numbers)
SERVO_PINS = [13, 12, 14, 27, 26]

# Servo angle limits [min_angle, max_angle] in degrees
SERVO_LIMITS = [
    (0, 180),   # Joint 0: Base rotation
    (15, 165),  # Joint 1: Shoulder (mechanical stops)
    (0, 180),   # Joint 2: Elbow
    (0, 180),   # Joint 3: Wrist pitch
    (0, 180),   # Joint 4: Wrist roll / gripper
]

# Home (neutral) position for each joint in degrees
SERVO_HOME = [90, 90, 90, 90, 90]

# PWM frequency for standard hobby servos (Hz)
SERVO_PWM_FREQ = 50

# Servo pulse width range in microseconds
# Standard: 1 ms = 0°/min, 2 ms = 180°/max; extended range used here
SERVO_MIN_PULSE_US = 500
SERVO_MAX_PULSE_US = 2500

# Main loop period in milliseconds
LOOP_DELAY_MS = 20
