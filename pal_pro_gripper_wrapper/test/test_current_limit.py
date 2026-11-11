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
"""Current limit of the grasper: over-current debounce, hold back-off, statistic lookup."""

from pal_pro_gripper_wrapper.gripper_grasper_srv import HoldGuard, OverCurrent, StatisticLookup
from pal_statistics_msgs.msg import StatisticsNames, StatisticsValues
import pytest


IDLE = 0.6       # A at rest (bag attach_2)
STIFFNESS = 400  # A per m the hold is pushed past the contact (made up, for the loop)


def test_over_current_needs_the_whole_time_above_the_limit():
    over = OverCurrent(2.0, 0.05)
    assert not over.update(0.00, 2.5)
    assert not over.update(0.04, 2.5)
    assert not over.update(0.045, 1.9)  # dropped below: start again
    assert not over.update(0.05, 2.5)
    assert over.update(0.10, -2.5)      # magnitude


def hold_on_contact(contact, start, push, max_backoff=0.005, steps=200):
    """Hold `start` against a contact at `contact`; current grows with how far past it."""
    guard = HoldGuard(start, push, OverCurrent(2.0, 0.05), 0.0005, max_backoff, 0.0, 0.07)
    sent = []
    for k in range(steps):
        depth = max(0.0, (contact - guard.position) * (1 if push < 0 else -1))
        # the controller applies each hold at once: its reference is the last one sent
        position = guard.update(k * 0.05, IDLE + STIFFNESS * depth, guard.position)
        if position is not None:
            sent.append(position)
    return guard, sent, IDLE + STIFFNESS * max(0.0, (contact - guard.position)
                                               * (1 if push < 0 else -1))


def test_grasp_backs_off_toward_open_until_under_the_limit():
    # holding 5 mm inside a 30 mm object: 0.6 + 2.0 A
    guard, sent, current = hold_on_contact(0.030, 0.025, push=-1)
    assert current <= 2.0
    assert all(b > a for a, b in zip([0.025] + sent, sent))  # only opens
    assert guard.backoff == pytest.approx(0.0015)            # 3 steps of 0.5 mm


def test_open_against_the_stop_backs_off_toward_closed():
    guard, sent, current = hold_on_contact(0.070, 0.074, push=+1)
    assert current <= 2.0 and sent and sent[-1] < 0.074


def test_back_off_stops_at_max_backoff():
    guard, sent, current = hold_on_contact(0.030, 0.020, push=-1, max_backoff=0.002)
    assert guard.exhausted and len(sent) == 4 and current > 2.0


def test_no_push_no_back_off():
    guard = HoldGuard(0.03, 0.0, OverCurrent(2.0, 0.0), 0.0005, 0.005, 0.0, 0.07)
    assert guard.update(0.0, 5.0, 0.03) is None


def test_late_commands_are_waited_for_before_the_next_step():
    # Robot, gripper_test2: the controller applied commands 0.25-1.1 s late. With the current
    # still high, one step per 50 ms would back off the whole 5 mm before the first one landed.
    guard = HoldGuard(0.025, -1, OverCurrent(2.0, 0.05), 0.0005, 0.005, 0.0, 0.07)
    reference, applied_at, steps = 0.025, None, []
    for k in range(40):
        t = k * 0.05
        position = guard.update(t, 3.0, reference)
        if position is not None:
            steps.append(t)
            applied_at = t + 0.5
        if applied_at is not None and t >= applied_at:
            reference = guard.position
    assert len(steps) == 4  # one per lag, not 10 in the first 0.5 s
    assert all(b - a > 0.5 for a, b in zip(steps, steps[1:]))


def test_the_contact_peak_settles_without_backing_off():
    # gripper_test3: after contact the current decays from -4.3 A to ~0 within ~1 s by itself
    guard = HoldGuard(0.0675, -1, OverCurrent(2.0, 0.05), 0.0005, 0.005, 0.0, 0.07, settle=1.0)
    for k in range(60):
        t = k * 0.05
        current = -4.3 * max(0.0, 1.0 - t / 0.9)  # unwinding
        assert guard.update(t, current, 0.0675) is None
    assert guard.backoff == 0.0


def test_a_lasting_over_current_backs_off_after_settling():
    guard = HoldGuard(0.0675, -1, OverCurrent(2.0, 0.05), 0.0005, 0.005, 0.0, 0.07, settle=1.0)
    steps = [k * 0.05 for k in range(60) if guard.update(k * 0.05, -3.0, guard.position)]
    assert steps and steps[0] >= 1.0                       # not during the settle time
    assert all(b - a >= 1.0 for a, b in zip(steps, steps[1:]))  # and again after each step


def test_statistic_found_by_a_pattern_matching_one_name():
    lookup = StatisticLookup('gripper.*current')
    names = ['arm_1_actuator_current', 'gripper_finger_actuator_current',
             'gripper_finger_actuator_temperature']
    lookup.set_names(StatisticsNames(names=names, names_version=3))
    assert lookup.name == 'gripper_finger_actuator_current'
    assert lookup.value(StatisticsValues(values=[1.0, 1.7, 50.0], names_version=3)) == 1.7
    with pytest.raises(LookupError):  # order may have changed
        lookup.value(StatisticsValues(values=[1.0, 1.7, 50.0], names_version=4))


def test_statistic_pattern_must_match_exactly_one():
    lookup = StatisticLookup('current')
    lookup.set_names(StatisticsNames(names=['a_current', 'b_current'], names_version=1))
    with pytest.raises(LookupError, match='matches 2'):
        lookup.value(StatisticsValues(values=[1.0, 2.0], names_version=1))
    lookup = StatisticLookup('gripper.*current')
    lookup.set_names(StatisticsNames(names=['motor_current', 'temp'], names_version=1))
    with pytest.raises(LookupError, match='motor_current'):  # lists the candidates
        lookup.value(StatisticsValues(values=[1.0, 2.0], names_version=1))
