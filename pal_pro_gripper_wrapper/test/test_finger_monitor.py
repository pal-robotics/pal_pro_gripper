# Copyright (c) 2026 PAL Robotics S.L. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Blocked/reached decisions of the grasper on a simulated finger (no ROS graph needed)."""

import pytest

from pal_pro_gripper_wrapper.gripper_grasper_srv import (BLOCKED, FingerMonitor, hold_position,
                                                         move_duration, REACHED)

DT = 0.01  # the node's monitor period


def run(start, target, duration, stop_at=None, lag=0.05, limit=4.0):
    """
    Simulate a move and return (outcome, time, finger position).

    Linear reference like the trajectory controller, the finger following it with a first-order
    lag and stopped by an obstacle at `stop_at`.
    """
    monitor = FingerMonitor(target, max_position_error=0.005, stall_motion=0.0005,
                            stall_time=0.1, reach_tolerance=0.001)
    finger, t = start, 0.0
    while t < limit:
        t += DT
        reference = start + (target - start) * min(t / duration, 1.0)
        finger += (reference - finger) * DT / lag
        if stop_at is not None:
            finger = max(finger, stop_at) if target < start else min(finger, stop_at)
        outcome = monitor.update(t, reference, finger)
        if outcome:
            return outcome, t, finger
    return None, t, finger


def test_free_close_reaches_without_blocking():
    outcome, t, finger = run(0.07, 0.0, 1.5)
    assert outcome == REACHED
    assert t == pytest.approx(1.5, abs=0.3)


def test_tracking_lag_while_moving_is_not_a_block():
    # 0.2 s lag at 0.047 m/s: ~9 mm behind the reference (> max error) but still moving
    outcome, _, _ = run(0.07, 0.0, 1.5, lag=0.2)
    assert outcome == REACHED


def test_an_object_blocks_the_close_where_it_is():
    outcome, t, finger = run(0.07, 0.0, 1.5, stop_at=0.03)
    contact = (0.07 - 0.03) / 0.07 * 1.5
    assert outcome == BLOCKED
    assert finger == pytest.approx(0.03, abs=1e-4)
    assert contact < t < contact + 0.35  # stall_time plus the lag before the finger stops


def test_a_target_past_the_mechanical_stop_blocks_instead_of_failing():
    outcome, _, finger = run(0.0, 0.077, 0.5, stop_at=0.07)
    assert outcome == BLOCKED
    assert finger == pytest.approx(0.07, abs=1e-4)


def test_already_holding_an_object_blocks_again_right_away():
    outcome, t, finger = run(0.03, 0.0, 1.5, stop_at=0.03)
    assert outcome == BLOCKED and t < 0.4


def test_move_duration_respects_the_finger_speed():
    assert move_duration(-0.077, 1.5, 0.03) == pytest.approx(0.077 / 0.03)  # full close: 2.6 s
    assert move_duration(0.009, 0.5, 0.03) == pytest.approx(0.5)  # short: the minimum time
    assert move_duration(0.077, 0.5, 0.0) == 0.5                  # no limit


def test_hold_position_squeezes_toward_the_target_only():
    assert hold_position(0.03, 0.0, 0.002, 0.0, 0.07) == pytest.approx(0.028)
    assert hold_position(0.001, 0.0, 0.002, 0.0, 0.07) == pytest.approx(0.0)  # never past it
    assert hold_position(0.07, 0.077, 0.0, 0.0, 0.077) == pytest.approx(0.07)  # open: no push
    assert hold_position(0.0705, 0.077, 0.002, 0.0, 0.07) == pytest.approx(0.07)  # in limits
