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

from dataclasses import dataclass
import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, SetLaunchConfiguration
from launch.substitutions import LaunchConfiguration
from launch_pal.arg_utils import LaunchArgumentsBase, read_launch_argument
from launch_pal.robot_arguments import CommonArgs
from launch_param_builder import load_xacro
from launch_ros.actions import Node
from pal_pro_gripper_description.launch_arguments import PalProGripperArgs


@dataclass(frozen=True)
class LaunchArguments(LaunchArgumentsBase):
    tool_changer: DeclareLaunchArgument = PalProGripperArgs.tool_changer
    use_sim_time: DeclareLaunchArgument = CommonArgs.use_sim_time
    sim_type: DeclareLaunchArgument = CommonArgs.sim_type
    mj_control: DeclareLaunchArgument = CommonArgs.mj_control
    world_name: DeclareLaunchArgument = CommonArgs.world_name


def declare_actions(launch_description: LaunchDescription, launch_args: LaunchArguments):

    launch_description.add_action(OpaqueFunction(
        function=create_robot_description_param))

    rsp = Node(package='robot_state_publisher',
               executable='robot_state_publisher',
               output='both',
               parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time'),
                            'robot_description': LaunchConfiguration('robot_description')}])

    launch_description.add_action(rsp)

    return


def generate_launch_description():

    # Create the launch description and populate
    ld = LaunchDescription()
    launch_arguments = LaunchArguments()

    launch_arguments.add_to_launch_description(ld)

    declare_actions(ld, launch_arguments)

    return ld


def create_robot_description_param(context):

    xacro_file_path = Path(os.path.join(
        get_package_share_directory('pal_pro_gripper_description'),
        'robots', 'pal_pro_gripper.urdf.xacro'))

    xacro_input_args = {
        'use_sim_time': read_launch_argument('use_sim_time', context),
        'tool_changer': read_launch_argument('tool_changer', context),
        'sim_type': read_launch_argument('sim_type', context),
        'mj_control': read_launch_argument('mj_control', context),
        'world_name': read_launch_argument('world_name', context),
    }
    robot_description = load_xacro(xacro_file_path, xacro_input_args)

    return [SetLaunchConfiguration('robot_description', robot_description)]
