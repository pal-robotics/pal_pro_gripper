# Copyright (c) 2024 PAL Robotics S.L. All rights reserved.
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

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_pal.arg_utils import LaunchArgumentsBase
from launch_pal.param_utils import parse_parametric_yaml
from launch_pal.robot_arguments import CommonArgs
from launch_ros.actions import Node


@dataclass(frozen=True)
class LaunchArguments(LaunchArgumentsBase):

    side: DeclareLaunchArgument = CommonArgs.side


def declare_actions(context, *args, **kwargs):

    side = LaunchConfiguration('side').perform(context)
    ee_prefix = 'gripper'
    if side:
        ee_prefix = f'gripper_{side}'

    remappings = {'EE_SIDE_PREFIX': ee_prefix}
    grasp_check_params = os.path.join(
        get_package_share_directory('pal_pro_gripper_wrapper'),
        'config', 'gripper.yaml')

    parsed_yaml = parse_parametric_yaml(source_files=[grasp_check_params],
                                        param_rewrites=remappings)

    grasp_check_srv = Node(
        package='pal_pro_gripper_wrapper',
        name=f'{ee_prefix}_grasper_srv',
        executable='gripper_grasper_srv',
        output='screen',
        emulate_tty=True,
        parameters=[parsed_yaml],
    )

    return [grasp_check_srv]


def generate_launch_description():

    # Create the launch description
    ld = LaunchDescription()

    launch_arguments = LaunchArguments()

    launch_arguments.add_to_launch_description(ld)

    ld.add_action(OpaqueFunction(function=declare_actions))

    return ld
