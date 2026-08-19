# Copyright (c) 2023 PAL Robotics S.L. All rights reserved.
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

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare

from dataclasses import dataclass
from launch_pal.arg_utils import LaunchArgumentsBase
from launch_pal.include_utils import include_scoped_launch_py_description
from launch_pal.robot_arguments import CommonArgs
from pal_pro_gripper_description.launch_arguments import PalProGripperArgs


@dataclass(frozen=True)
class LaunchArguments(LaunchArgumentsBase):
    tool_changer: DeclareLaunchArgument = PalProGripperArgs.tool_changer
    use_sim_time: DeclareLaunchArgument = CommonArgs.use_sim_time


def generate_launch_description():

    # Create the launch description and populate
    ld = LaunchDescription()
    launch_arguments = LaunchArguments()

    launch_arguments.add_to_launch_description(ld)

    declare_actions(ld, launch_arguments)

    return ld


def declare_actions(launch_description: LaunchDescription, launch_args: LaunchArguments):

    robot_state_publisher = include_scoped_launch_py_description(
        pkg_name='pal_pro_gripper_description',
        paths=['launch', 'robot_state_publisher.launch.py'],
        launch_arguments={'use_sim_time': LaunchConfiguration('use_sim_time'),
                          'tool_changer': LaunchConfiguration('tool_changer'),
                          })

    launch_description.add_action(robot_state_publisher)

    start_joint_pub_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen')

    launch_description.add_action(start_joint_pub_gui)

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare('pal_pro_gripper_description'), 'config', 'show.rviz'])

    start_rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}])

    launch_description.add_action(start_rviz_cmd)

    return
