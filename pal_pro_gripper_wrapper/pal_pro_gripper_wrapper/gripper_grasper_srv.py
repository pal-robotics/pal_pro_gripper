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

import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.duration import Duration
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool
from std_srvs.srv import Empty
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


class GripperGrasper(Node):

    def __init__(self) -> None:
        super().__init__('gripper_grasper_srv',
                         automatically_declare_parameters_from_overrides=True)

        # Init Params and Subscriptions - defaults
        self.init_params()
        self.init_subscriptions()
        self.get_logger().info(f'{self.get_name()} initialized. Ready..')

    def init_params(self) -> None:
        self.last_state = None
        self.controller_name = self.get_parameter(
            'controller_name').get_parameter_value().string_value
        self.joint_names = self.get_parameter(
            'joint_names').get_parameter_value().string_array_value
        self.max_position_error = self.get_parameter(
            'max_position_error').get_parameter_value().double_value
        self.timeout = self.get_parameter(
            'timeout').get_parameter_value().double_value
        self.opening_time = self.get_parameter(
            'opening_time').get_parameter_value().double_value
        self.closing_time = self.get_parameter(
            'closing_time').get_parameter_value().double_value
        self.open_value = self.get_parameter(
            'open_value').get_parameter_value().double_array_value
        self.close_value = self.get_parameter(
            'close_value').get_parameter_value().double_array_value
        self.rate = self.get_parameter('rate').get_parameter_value().double_value
        self.is_grasped = Bool()
        self.is_grasped.data = False

        # Define if the gripper grasping without stressing the joint
        # applying the 'optimal_close' joint value
        self.has_grasped_object = False
        # True when it's open, False otherwise
        self.is_open = False

    def init_subscriptions(self) -> None:

        # Used to let the cb in the group to run concurrently
        self.cb_group = ReentrantCallbackGroup()

        # Subs to gripper state
        self.state_sub = self.create_subscription(
            JointState, '/joint_states',
            self.state_cb, qos_profile=1, callback_group=self.cb_group)
        # Publisher on the gripper topic
        self.cmd_pub = self.create_publisher(
            JointTrajectory, f'/{self.controller_name}/joint_trajectory', 10)
        self.get_logger().info(f'Publishing on topic: {self.cmd_pub.topic_name}')

        # Graspng srv to offer
        self.grasp_srv = self.create_service(
            Empty, f'/{self.get_name()}/grasp', self.grasp_cb, callback_group=self.cb_group)
        self.get_logger().info(f'Offering grasp srv on: {self.grasp_srv.srv_name}')

        # Releasing srv to offer
        self.release_srv = self.create_service(
            Empty, f'/{self.get_name()}/release', self.open_cb)
        self.get_logger().info(f'Offering release srv on: {self.release_srv.srv_name}')

        # Publish the grasp state each 'rate' secons to know if an object is grasped or not
        self.pub_grasp_state = self.create_publisher(Bool, f'{self.get_name()}/is_grasped', 10)
        self.pub_state_timer = self.create_timer(self.rate, self.publish_grasping_state)
        self.get_logger().info(
            f'Publishing on topic: {self.pub_grasp_state.topic_name} each {self.rate} seconds.')

    def state_cb(self, msg: JointState) -> None:
        # check /joint_state msg structure
        idx = -1
        for i, name in enumerate(msg.name):
            if name in self.joint_names:
                idx = i
                break
        if idx == -1:
            self.get_logger().error(f'Gripper joint: {self.joint_names} not present in '
                                    '/joint_states topic.')
            rclpy.shutdown()

        self.last_state = msg.position[idx]

    def publish_grasping_state(self) -> None:
        self.is_grasped.data = self.has_grasped_object
        # Publishing state
        self.pub_grasp_state.publish(self.is_grasped)

    def open_cb(self, req: Empty.Request, res: Empty.Response) -> Empty.Response:
        self.get_logger().info('Recieved open request')

        # In any case we open the gripper
        # Handle the case if the srv is called again after a successfull grasp
        if not self.is_open:
            self.send_joint_traj(self.open_value, self.opening_time)
            self.get_clock().sleep_for(Duration(seconds=self.opening_time))
            self.has_grasped_object = False
            self.is_open = True

        self.get_logger().info('Gripper opened!\n')
        return res

    def grasp_cb(self, req: Empty.Request, res: Empty.Response) -> Empty.Response:
        self.get_logger().info('Recieved grasp request')

        # Keep closing the gripper until the error of the state reaches
        # max_position_error or any of the gripper joints (or timeout)
        init_time = self.get_clock().now()
        close_val = self.close_value

        # Handle the case if the srv is called again after a successfull grasp
        if not self.has_grasped_object:
            self.send_joint_traj(close_val, self.closing_time)
            self.get_clock().sleep_for(Duration(seconds=self.closing_time))
            self.is_open = False

        object_detected = False
        while rclpy.ok() and (self.get_clock().now()-init_time) < Duration(seconds=self.timeout):

            if self.last_state is None:
                self.get_logger().warning('Waiting for gripper state...')
                continue

            current_error = self.last_state - close_val[0]

            # If the position error is > than a treshold means something
            # is within the gripper: it grasped
            if not object_detected and abs(current_error) > self.max_position_error:
                object_detected = True
                self.has_grasped_object = True
                close_val = self.get_optimal_close()
                self.send_joint_traj(close_val, self.closing_time)
                break

        self.get_logger().info('Gripper closed!\n')
        return res

    # Get optimal value to close the gripper to not let the joint stress in case of grasp
    def get_optimal_close(self) -> list[float]:
        optimal_close = self.last_state
        # range: [close_value, open_value]
        optimal_close = max(min(self.open_value[0], optimal_close), self.close_value[0])
        self.get_logger().info(f'Optimal close: {optimal_close}')
        return [optimal_close]

    def send_joint_traj(self, j_positions: list[float], exec_time: float) -> None:
        jt = JointTrajectory()
        jt.joint_names = self.joint_names
        p = JointTrajectoryPoint()
        p.positions = j_positions
        p.time_from_start = Duration(seconds=exec_time).to_msg()
        jt.points.append(p)

        self.get_logger().info('Sending: ' + str(j_positions[0]))
        self.cmd_pub.publish(jt)
        return


def main(args=None):
    rclpy.init()
    gg = GripperGrasper()
    executor = MultiThreadedExecutor()

    executor.add_node(gg)
    executor.spin()


if __name__ == '__main__':
    main()
