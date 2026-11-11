# Copyright 2026 ERDI Technology
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Launch one ERDI laser rangefinder node."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    """Return the launch description."""
    args = {
        'port': '/dev/ttyUSB0',
        'model': 'LRF3000A1',
        'baud': '0',
        'frame_id': 'erdi_lrf_link',
        'rate': '10.0',
        'field_of_view': '0.0',
    }
    decls = [DeclareLaunchArgument(k, default_value=v)
             for k, v in args.items()]
    node = Node(
        package='erdi_lrf_driver',
        executable='erdi_lrf_node',
        name='erdi_lrf_node',
        output='screen',
        parameters=[{
            'port': ParameterValue(LaunchConfiguration('port'), value_type=str),
            'model': ParameterValue(LaunchConfiguration('model'), value_type=str),
            'baud': ParameterValue(LaunchConfiguration('baud'), value_type=int),
            'frame_id': ParameterValue(
                LaunchConfiguration('frame_id'), value_type=str),
            'rate': ParameterValue(LaunchConfiguration('rate'), value_type=float),
            'field_of_view': ParameterValue(
                LaunchConfiguration('field_of_view'), value_type=float),
        }],
    )
    return LaunchDescription(decls + [node])
