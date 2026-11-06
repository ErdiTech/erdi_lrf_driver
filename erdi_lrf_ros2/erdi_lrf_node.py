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

"""Publish an ERDI UART laser rangefinder as sensor_msgs/msg/Range."""

import math

from erdi_lrf_ros2._erdi_lrf import ErdiLRF, ErdiLrfError, get_model
from erdi_lrf_ros2._erdi_lrf.models import field_of_view_rad
from rcl_interfaces.msg import ParameterDescriptor
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Range


class ErdiLrfNode(Node):
    """Poll one ERDI module at ``rate`` Hz and publish ``Range`` messages."""

    def __init__(self, serial_factory=None, parameter_overrides=None):
        """Create the node; ``serial_factory`` lets tests inject a fake port."""
        super().__init__(
            'erdi_lrf_node', parameter_overrides=parameter_overrides)
        ro = ParameterDescriptor(read_only=True)
        self.declare_parameter('port', '/dev/ttyUSB0', ro)
        self.declare_parameter('model', 'LRF3000A1', ro)
        self.declare_parameter('baud', 0, ro)  # 0 = model default
        self.declare_parameter('frame_id', 'erdi_lrf_link')
        self.declare_parameter('rate', 10.0, ro)
        self.declare_parameter('timeout', 0.5, ro)
        # 0.0 = take the value from the model table
        self.declare_parameter('min_range', 0.0)
        self.declare_parameter('max_range', 0.0)
        # Full beam divergence in radians. 0.0 = use the per-model value from
        # the published specification table (fallback 0.002 if the model has
        # no divergence row).
        self.declare_parameter('field_of_view', 0.0)
        # Stream continuously instead of one request per tick.
        self.declare_parameter('continuous', False, ro)
        # Required on LRF1200A1 / LRF3000A1, whose manuals leave the
        # continuous-reply function byte unresolved.
        self.declare_parameter('acknowledge_protocol_hold', False, ro)
        self.declare_parameter('topic', 'range', ro)

        model = self.get_parameter('model').value
        self._spec = get_model(model)
        if self._spec.metres_per_count is None:
            raise RuntimeError(
                f'{self._spec.model}: the manual publishes no distance '
                'scaling, so a sensor_msgs/Range in metres cannot be produced '
                'honestly. Ask ERDI to confirm the scaling: '
                'https://erdilrf.com/contact/')
        baud = int(self.get_parameter('baud').value) or None
        self._lrf = ErdiLRF(
            self.get_parameter('port').value, model=model, baud=baud,
            timeout=float(self.get_parameter('timeout').value),
            serial_factory=serial_factory)

        rate = float(self.get_parameter('rate').value)
        if rate <= 0.0:
            raise ValueError('parameter "rate" must be > 0')
        self._stream = None
        if self.get_parameter('continuous').value:
            self._stream = self._lrf.stream(
                acknowledge_protocol_hold=bool(
                    self.get_parameter('acknowledge_protocol_hold').value))
        self._pub = self.create_publisher(
            Range, self.get_parameter('topic').value, qos_profile_sensor_data)
        self._timer = self.create_timer(1.0 / rate, self._tick)
        self.get_logger().info(
            f'{model} on {self.get_parameter("port").value} '
            f'(protocol family {self._spec.family}), {rate:g} Hz')

    def _limits(self):
        lo = float(self.get_parameter('min_range').value) or \
            self._spec.min_range_m or 0.0
        hi = float(self.get_parameter('max_range').value) or \
            self._spec.max_range_m or float('inf')
        return lo, hi

    def build_message(self, metres):
        """Build a Range message using REP-117 semantics for invalid data."""
        lo, hi = self._limits()
        msg = Range()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.get_parameter('frame_id').value
        msg.radiation_type = Range.INFRARED
        fov = float(self.get_parameter('field_of_view').value)
        msg.field_of_view = fov if fov > 0.0 else field_of_view_rad(
            self._spec.model)
        msg.min_range = float(lo)
        msg.max_range = float(hi)
        if metres is None or math.isnan(metres):
            msg.range = float('nan')
        elif metres < lo:
            msg.range = float('-inf')
        elif metres > hi:
            msg.range = float('inf')
        else:
            msg.range = float(metres)
        return msg

    def _tick(self):
        try:
            if self._stream is not None:
                m = next(self._stream)
            elif self._spec.family == 'B':
                # free-running stream: drop stale frames, take the next one
                self._lrf.ser.reset_input_buffer()
                m = self._lrf.measure(raise_on_failure=False)
            else:
                m = self._lrf.measure(raise_on_failure=False)
        except StopIteration:
            self._stop_stream('continuous stream ended; restart the node')
            return
        except ErdiLrfError as exc:
            if self._stream is not None:
                self._stop_stream(f'continuous stream stopped: {exc}')
                return
            self.get_logger().warning(
                f'measurement error: {exc}', throttle_duration_sec=5.0)
            return
        if getattr(m, 'out_of_range', False):
            metres = float('inf')
        elif getattr(m, 'ok', True):
            metres = m.metres
        else:
            metres = float('nan')
        self._pub.publish(self.build_message(metres))

    def _stop_stream(self, reason):
        stream, self._stream = self._stream, None
        self._timer.cancel()
        try:
            if stream is not None:
                stream.close()
        except Exception as exc:  # noqa: BLE001 - cleanup must not raise
            self.get_logger().warning(f'stream cleanup failed: {exc}')
        self.get_logger().warning(reason)

    def destroy_node(self):
        """Close the serial port, then destroy the node."""
        try:
            if self._stream is not None:
                self._stream.close()
        finally:
            self._close_and_destroy()

    def _close_and_destroy(self):
        try:
            self._lrf.close()
        finally:
            super().destroy_node()


def main(args=None):
    """Run the ``erdi_lrf_node`` executable."""
    rclpy.init(args=args)
    node = ErdiLrfNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
