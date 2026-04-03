"""Unit tests for the RoboticArm controller."""

import pytest
from arm.arm_controller import RoboticArm
from arm import config


# ---------------------------------------------------------------------------
# RoboticArm
# ---------------------------------------------------------------------------

class TestRoboticArm:
    def test_init_creates_correct_number_of_servos(self):
        arm = RoboticArm()
        assert len(arm._servos) == RoboticArm.NUM_JOINTS

    def test_home_sets_all_joints_to_home_angles(self):
        arm = RoboticArm()
        arm.home()
        assert arm.get_angles() == config.SERVO_HOME

    def test_move_joint_sets_angle(self):
        arm = RoboticArm()
        arm.move_joint(RoboticArm.JOINT_ELBOW, 60.0)
        angles = arm.get_angles()
        assert angles[RoboticArm.JOINT_ELBOW] == 60.0

    def test_move_joint_out_of_range_raises(self):
        arm = RoboticArm()
        with pytest.raises(IndexError):
            arm.move_joint(10, 90.0)

    def test_move_joint_negative_index_raises(self):
        arm = RoboticArm()
        with pytest.raises(IndexError):
            arm.move_joint(-1, 90.0)

    def test_move_all_sets_all_joints(self):
        arm = RoboticArm()
        targets = [10.0, 20.0, 30.0, 40.0, 50.0]
        arm.move_all(targets)
        assert arm.get_angles() == targets

    def test_move_all_ignores_extra_values(self):
        arm = RoboticArm()
        targets = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
        arm.move_all(targets)
        assert arm.get_angles() == targets[:RoboticArm.NUM_JOINTS]

    def test_move_all_partial_leaves_others_unchanged(self):
        arm = RoboticArm()
        arm.home()
        arm.move_all([15.0, 30.0])
        angles = arm.get_angles()
        assert angles[0] == 15.0
        assert angles[1] == 30.0
        # Remaining joints should still be at home
        assert angles[2] == config.SERVO_HOME[2]

    def test_joint_constants_are_correct(self):
        assert RoboticArm.JOINT_BASE == 0
        assert RoboticArm.JOINT_SHOULDER == 1
        assert RoboticArm.JOINT_ELBOW == 2
        assert RoboticArm.JOINT_WRIST_PITCH == 3
        assert RoboticArm.JOINT_WRIST_ROLL == 4

    def test_servo_limits_applied(self):
        arm = RoboticArm()
        min_a, max_a = config.SERVO_LIMITS[RoboticArm.JOINT_SHOULDER]
        # Try to move beyond max
        arm.move_joint(RoboticArm.JOINT_SHOULDER, max_a + 50)
        assert arm.get_angles()[RoboticArm.JOINT_SHOULDER] == max_a

    def test_deinit_does_not_raise(self):
        arm = RoboticArm()
        arm.deinit()  # should not raise
