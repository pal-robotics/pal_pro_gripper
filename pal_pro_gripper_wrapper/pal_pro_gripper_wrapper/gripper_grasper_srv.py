# Copyright (c) 2025 PAL Robotics S.L. All rights reserved.
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
"""
Grasp and release the PAL Pro gripper without leaving the finger pushing on something.

Srv: /<node>/grasp    std_srvs/Empty: close until the finger is blocked (an object, or fully
                      closed), then hold `grasp_squeeze` further closed than where it stopped
     /<node>/release  std_srvs/Empty: open; if blocked on the way, hold where it stopped
Pub: <node>/is_grasped  std_msgs/Bool at `rate` Hz and after every grasp/release
In:  /<controller>/controller_state  control_msgs/JointTrajectoryControllerState
     <current_topic> (+ its /names)  pal_statistics_msgs/StatisticsValues: the motor current
Out: /<controller>/joint_trajectory  trajectory_msgs/JointTrajectory

Why: the trajectory controller drives the finger to the commanded position. If something stops
it (an object, or a target past the mechanical stop) the error stays, the actuator keeps pushing
(current up, it overheats) and, goal_time after the end of the trajectory with the error above the
goal tolerance, the controller gives up ("Exceeded goal_time_tolerance: holding position...").

Blocked: the finger lags the commanded (reference) position by more than `max_position_error`
while it moved less than `stall_motion` in the last `stall_time` s, or |current| has been above
`max_current` for `current_time` s. Then a new goal holds it there.
Current limit while holding: |current| above `max_current` for `current_time` s backs the hold
position off by `backoff_step` from what the finger pushes on, up to `max_backoff` in total.
Without current data (empty `current_statistic`, or no topic, e.g. in simulation) only the
position is used.
"""

from collections import deque
import math
import re
import threading
import time
from typing import Any

from control_msgs.msg import JointTrajectoryControllerState
from pal_statistics_msgs.msg import StatisticsNames, StatisticsValues
import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.duration import Duration
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import DurabilityPolicy, qos_profile_sensor_data, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Bool
from std_srvs.srv import Empty
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

REACHED, BLOCKED, TIMEOUT, NO_STATE = 'reached', 'blocked', 'timeout', 'no controller state'
# How pal_statistics publishes <topic>/names (latched); the values are best effort
STATISTICS_NAMES_QOS = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                                  reliability=ReliabilityPolicy.RELIABLE)


class FingerMonitor:
    """Tell when a move of the finger is over: it REACHED the target or got BLOCKED before it."""

    def __init__(self, target, max_position_error, stall_motion, stall_time, reach_tolerance):
        self.target = target
        self._max_error = max_position_error
        self._stall_motion = stall_motion
        self._stall_time = stall_time
        self._reach_tolerance = reach_tolerance
        self._history = deque()  # (t, feedback) covering the last stall_time s

    def update(self, t, reference, feedback):
        """Return None while moving, REACHED or BLOCKED once the move is over."""
        if (abs(reference - self.target) <= self._reach_tolerance
                and abs(feedback - self.target) <= self._reach_tolerance):
            return REACHED
        self._history.append((t, feedback))
        while len(self._history) > 1 and self._history[1][0] <= t - self._stall_time:
            self._history.popleft()
        window = [f for _, f in self._history]
        stalled = (self._history[0][0] <= t - self._stall_time
                   and max(window) - min(window) < self._stall_motion)
        if stalled and abs(reference - feedback) > self._max_error:
            return BLOCKED
        return None


class OverCurrent:
    """Tell when |current| has stayed above max_current for over_time s."""

    def __init__(self, max_current, over_time):
        self.max_current = max_current
        self._over_time = over_time
        self._since = None

    def reset(self):
        self._since = None

    def update(self, t, current):
        if abs(current) <= self.max_current:
            self._since = None
            return False
        if self._since is None:
            self._since = t
        return t - self._since >= self._over_time


class HoldGuard:
    """While holding, back off from what the finger pushes on while the current is too high."""

    def __init__(self, position, push, over_current, step, max_backoff, low, high):
        self.position = position
        self._push = math.copysign(1.0, push) if push else 0.0  # direction it pushes in
        self._over = over_current
        self._step = step
        self._max_backoff = max_backoff
        self._low, self._high = low, high
        self.backoff = 0.0

    @property
    def exhausted(self):
        return self.backoff + self._step > self._max_backoff + 1e-12

    def update(self, t, current):
        """Return a new hold position to send, or None to keep the current one."""
        if not self._push or not self._over.update(t, current) or self.exhausted:
            return None
        self._over.reset()  # the next step needs current_time over the limit again
        self.backoff += self._step
        self.position = min(max(self.position - self._push * self._step, self._low), self._high)
        return self.position


class StatisticLookup:
    """One pal_statistics value, found by a regular expression that matches one name."""

    def __init__(self, pattern):
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.version = None
        self.name = None
        self._index = None
        self.problem = 'no names received yet'

    def set_names(self, msg):
        self.version = msg.names_version
        matches = [i for i, name in enumerate(msg.names) if self.pattern.search(name)]
        if len(matches) == 1:
            self._index, self.name = matches[0], msg.names[matches[0]]
            return
        self._index = self.name = None
        found = [msg.names[i] for i in matches] or [
            n for n in msg.names if 'current' in n.lower()]
        self.problem = (f"'{self.pattern.pattern}' matches {len(matches)} of the names (version "
                        f'{self.version}), it must match one. Candidates: {found[:10]}')

    def value(self, msg):
        """Return the value in a StatisticsValues `msg`; LookupError if it can't."""
        if self._index is None:
            raise LookupError(self.problem)
        if msg.names_version != self.version:
            raise LookupError(f'values have names_version {msg.names_version}, names '
                              f'{self.version}')
        return float(msg.values[self._index])


def move_duration(distance, min_time, max_speed):
    """Return the time for a move: at least min_time, and no faster than max_speed (if > 0)."""
    return max(min_time, abs(distance) / max_speed) if max_speed > 0 else min_time


def hold_position(stop, target, squeeze, low, high):
    """
    Return where to hold a finger blocked at `stop` on its way to `target`.

    That is `squeeze` further toward the target (never past it), within [low, high].
    """
    step = min(squeeze, abs(target - stop))
    return min(max(stop + math.copysign(step, target - stop), low), high)


class GripperGrasper(Node):

    def __init__(self) -> None:
        super().__init__('gripper_grasper_srv',
                         automatically_declare_parameters_from_overrides=True)

        def param(name, default=None) -> Any:
            """Return parameter `name`: required (no default) or `default` when not set."""
            if default is None:
                value = self.get_parameter(name).value
            else:
                value = self.get_parameter_or(name, Parameter(name, value=default)).value
            if value is None:
                raise ValueError(f"Parameter '{name}' is not set")
            return value

        self.controller_name = param('controller_name')
        self.joint_names = list(param('joint_names'))
        if len(self.joint_names) != 1:
            raise ValueError(f'One actuated finger joint expected, not {self.joint_names}')
        self.open_value = float(param('open_value')[0])
        self.close_value = float(param('close_value')[0])
        self.opening_time = float(param('opening_time'))
        self.closing_time = float(param('closing_time'))
        self.timeout = float(param('timeout'))   # s after the move's time to give up
        self.max_speed = float(param('max_speed', 0.03))  # joint units/s, 0: no limit
        self.max_position_error = float(param('max_position_error'))
        self.stall_motion = float(param('stall_motion', 0.0005))
        self.stall_time = float(param('stall_time', 0.1))
        self.grasp_squeeze = float(param('grasp_squeeze', 0.002))
        self.empty_tolerance = float(param('empty_tolerance', 0.003))
        self.reach_tolerance = float(param('reach_tolerance', 0.001))
        self.hold_time = float(param('hold_time', 0.2))
        self.period = 1.0 / float(param('monitor_rate', 100.0))
        self.low, self.high = sorted((self.open_value, self.close_value))
        current_topic = param('current_topic', '/actuators_statistics/values')
        current_statistic = param('current_statistic', '')
        self.max_current = float(param('max_current', 2.0))
        self.current_time = float(param('current_time', 0.05))
        self.backoff_step = float(param('backoff_step', 0.0005))
        self.max_backoff = float(param('max_backoff', 0.005))

        self.has_grasped_object = False
        self._state = None    # (receive time [s], reference, feedback) of the finger joint
        self._current = None  # (receive time [s], current [A])
        self._guard = None    # HoldGuard of the position held now
        self._lock = threading.Lock()  # one move at a time

        group = ReentrantCallbackGroup()
        self.state_topic = f'/{self.controller_name}/controller_state'
        self.create_subscription(JointTrajectoryControllerState, self.state_topic,
                                 self.state_cb, qos_profile_sensor_data, callback_group=group)
        self._current_lookup = None
        if current_statistic:
            if not current_topic.endswith('/values'):
                raise ValueError(f"current_topic must end in '/values', not '{current_topic}'")
            self.current_topic = current_topic
            lookup = self._current_lookup = StatisticLookup(current_statistic)

            def on_names(msg: StatisticsNames) -> None:
                self.current_names_cb(lookup, msg)

            def on_values(msg: StatisticsValues) -> None:
                self.current_cb(lookup, msg)

            self.create_subscription(StatisticsNames, current_topic[:-len('values')] + 'names',
                                     on_names, STATISTICS_NAMES_QOS, callback_group=group)
            self.create_subscription(StatisticsValues, current_topic, on_values,
                                     qos_profile_sensor_data, callback_group=group)
            self.create_timer(0.05, self.guard_cb, callback_group=group)
        self.cmd_pub = self.create_publisher(
            JointTrajectory, f'/{self.controller_name}/joint_trajectory', 10)
        self.grasp_srv = self.create_service(
            Empty, f'/{self.get_name()}/grasp', self.grasp_cb, callback_group=group)
        self.release_srv = self.create_service(
            Empty, f'/{self.get_name()}/release', self.open_cb, callback_group=group)
        self.pub_grasp_state = self.create_publisher(Bool, f'{self.get_name()}/is_grasped', 10)
        self.create_timer(1.0 / float(param('rate')), self.publish_grasping_state)
        limit = (f'current limit {self.max_current} A ({current_topic} ~ '
                 f"'{current_statistic}')" if current_statistic else 'no current limit')
        self.get_logger().info(
            f'Ready: {self.grasp_srv.srv_name}, {self.release_srv.srv_name} '
            f'({self.state_topic} -> {self.cmd_pub.topic_name}), {limit}')

    def now(self) -> float:
        return self.get_clock().now().nanoseconds * 1e-9

    def state_cb(self, msg: JointTrajectoryControllerState) -> None:
        try:
            i = list(msg.joint_names).index(self.joint_names[0])
            self._state = (self.now(), msg.reference.positions[i], msg.feedback.positions[i])
        except (ValueError, IndexError):
            self.get_logger().warn(f'No {self.joint_names[0]} position in {self.state_topic}',
                                   throttle_duration_sec=5.0)

    def current_names_cb(self, lookup: StatisticLookup, msg: StatisticsNames) -> None:
        lookup.set_names(msg)
        if lookup.name is None:
            self.get_logger().error(f'No current: {lookup.problem}')
        else:
            self.get_logger().info(f"Current from '{lookup.name}'")

    def current_cb(self, lookup: StatisticLookup, msg: StatisticsValues) -> None:
        try:
            self._current = (self.now(), abs(lookup.value(msg)))
        except (LookupError, IndexError) as error:
            self.get_logger().warn(f'No current: {error}', throttle_duration_sec=5.0)

    def current_now(self):
        """Return the latest |current| [A], or None without recent data."""
        current = self._current
        if current is None or self.now() - current[0] > 0.5:
            return None
        return current[1]

    def publish_grasping_state(self) -> None:
        self.pub_grasp_state.publish(Bool(data=self.has_grasped_object))

    def open_cb(self, _req: Empty.Request, res: Empty.Response) -> Empty.Response:
        self.get_logger().info('Received release request')
        with self._lock:
            outcome, stop = self.move(self.open_value, self.opening_time, squeeze=0.0)
            self.has_grasped_object = False
            self.publish_grasping_state()
        if outcome == BLOCKED:
            self.get_logger().warn(f'Opening blocked at {stop:.4f} before {self.open_value:.4f}'
                                   ' (obstacle or mechanical stop): holding there')
        self.get_logger().info(f'Release: {outcome}')
        return res

    def grasp_cb(self, _req: Empty.Request, res: Empty.Response) -> Empty.Response:
        self.get_logger().info('Received grasp request')
        with self._lock:
            outcome, stop = self.move(self.close_value, self.closing_time, self.grasp_squeeze)
            self.has_grasped_object = (
                stop is not None and abs(stop - self.close_value) > self.empty_tolerance)
            self.publish_grasping_state()
        where = '' if stop is None else f' at {stop:.4f}'
        self.get_logger().info(f'Grasp: {outcome}{where}, '
                               f'{"object grasped" if self.has_grasped_object else "nothing"}')
        return res

    def move(self, target: float, duration: float, squeeze: float):
        """
        Move the finger to `target`; if blocked, hold `squeeze` past where it stopped.

        Return (REACHED | BLOCKED | TIMEOUT | NO_STATE, position where it stopped or None).
        """
        self._guard = None
        start = self.now()
        if self._state is None or start - self._state[0] > 0.5:
            self.get_logger().error(f'No recent {self.state_topic}: not moving')
            return NO_STATE, None
        if self._current_lookup is not None and self.current_now() is None:
            self.get_logger().warn(f'No current from {self.current_topic}: position only')
        origin = self._state[2]
        duration = move_duration(target - origin, duration, self.max_speed)
        self.send_joint_traj(target, duration)
        monitor = FingerMonitor(target, self.max_position_error, self.stall_motion,
                                self.stall_time, self.reach_tolerance)
        over = OverCurrent(self.max_current, self.current_time)
        deadline = start + duration + self.timeout
        last = None
        while rclpy.ok():
            time.sleep(self.period)
            stamp, reference, feedback = self._state
            if stamp == last or stamp <= start:
                if self.now() - stamp > 0.5:
                    self.get_logger().error(f'{self.state_topic} stopped: holding')
                    self.send_joint_traj(self._state[2], self.hold_time)
                    return NO_STATE, self._state[2]
                continue
            last = stamp
            outcome = monitor.update(stamp, reference, feedback)
            current = self.current_now()
            if current is not None and over.update(stamp, current):
                outcome, squeeze = BLOCKED, 0.0  # already pushing hard: no extra squeeze
                self.get_logger().info(f'Current {current:.2f} A > {self.max_current} A')
            if outcome == REACHED:
                self.hold(target, target - origin)
                return REACHED, feedback
            if outcome == BLOCKED or stamp > deadline:
                hold = hold_position(feedback, target, squeeze, self.low, self.high)
                self.send_joint_traj(hold, self.hold_time)
                self.hold(hold, target - feedback)
                self.get_logger().info(f'Stopped at {feedback:.4f} (commanded {reference:.4f}),'
                                       f' holding {hold:.4f}')
                return (BLOCKED if outcome == BLOCKED else TIMEOUT), feedback
        return TIMEOUT, None

    def hold(self, position: float, push: float) -> None:
        """Watch the current while holding `position`, pushing in the direction of `push`."""
        if self._current_lookup is not None:
            self._guard = HoldGuard(position, push, OverCurrent(self.max_current,
                                                                self.current_time),
                                    self.backoff_step, self.max_backoff, self.low, self.high)

    def guard_cb(self) -> None:
        if not self._lock.acquire(blocking=False):  # a move is running: it watches the current
            return
        try:
            guard, current = self._guard, self.current_now()
            if guard is None or current is None:
                return
            position = guard.update(self.now(), current)
            if position is not None:
                self.send_joint_traj(position, self.hold_time)
                self.get_logger().warn(f'Current {current:.2f} A > {self.max_current} A: '
                                       f'holding {position:.4f} ({guard.backoff * 1e3:.1f} mm '
                                       'back)')
            elif guard.exhausted and current > self.max_current:
                self.get_logger().error(
                    f'Current {current:.2f} A > {self.max_current} A after backing off '
                    f'{guard.backoff * 1e3:.1f} mm (max_backoff)', throttle_duration_sec=5.0)
        finally:
            self._lock.release()

    def send_joint_traj(self, position: float, exec_time: float) -> None:
        point = JointTrajectoryPoint(positions=[float(position)],
                                     time_from_start=Duration(
                                         nanoseconds=int(exec_time * 1e9)).to_msg())
        self.cmd_pub.publish(JointTrajectory(joint_names=self.joint_names, points=[point]))


def main(args=None):
    rclpy.init(args=args)
    gg = GripperGrasper()
    executor = MultiThreadedExecutor()
    executor.add_node(gg)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        gg.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
