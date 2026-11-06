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

"""Run the node against a fake family-A serial port (no hardware)."""

import math

from erdi_lrf_ros2._erdi_lrf import protocol_a as pa
from erdi_lrf_ros2.erdi_lrf_node import ErdiLrfNode
import pytest
import rclpy
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Range


class FakeSerial:
    """Answers every 55 AA 88 single-shot request with a fixed distance."""

    def __init__(self, port, baud, timeout, raw=12345, status=0x01):
        self.port, self.baud, self.timeout = port, baud, timeout
        self.raw, self.status = raw, status
        self.rx = bytearray()
        self.closed = False

    def write(self, data):
        if bytes(data) == pa.single_shot():
            body = bytes([0x55, 0xAA, pa.FN_SINGLE, self.status, 0xFF,
                          self.raw >> 8, self.raw & 0xFF])
            self.rx += body + bytes([pa.rx_checksum(body)])
        elif bytes(data) == pa.continuous():
            body = bytes([0x55, 0xAA, pa.FN_CONTINUOUS, self.status, 0xFF,
                          self.raw >> 8, self.raw & 0xFF])
            self.rx += (body + bytes([pa.rx_checksum(body)])) * 3
        return len(data)

    def read(self, n=1):
        out = bytes(self.rx[:n])
        del self.rx[:n]
        return out

    def reset_input_buffer(self):
        self.rx.clear()

    def close(self):
        self.closed = True


@pytest.fixture(autouse=True)
def ros_context():
    rclpy.init()
    yield
    rclpy.shutdown()


def make_node(raw, status=0x01, extra=None):
    ports = []

    def factory(port, baud, timeout):
        ports.append(FakeSerial(port, baud, timeout, raw, status))
        return ports[-1]

    overrides = [Parameter('model', value='LRF3000A1'),
                 Parameter('frame_id', value='laser'),
                 Parameter('rate', value=50.0)] + (extra or [])
    node = ErdiLrfNode(serial_factory=factory, parameter_overrides=overrides)
    return node, ports[0]


def collect(node, count=1):
    got = []
    sub_node = rclpy.create_node('listener')
    sub_node.create_subscription(
        Range, 'range', got.append,
        qos_profile_sensor_data)
    for _ in range(count):
        node._tick()
    for _ in range(50):
        rclpy.spin_once(sub_node, timeout_sec=0.05)
        if len(got) >= count:
            break
    sub_node.destroy_node()
    return got


def test_publishes_range_from_fake_port():
    node, port = make_node(raw=12345)  # 1234.5 m
    try:
        got = collect(node)
    finally:
        node.destroy_node()
    assert port.closed
    assert len(got) == 1
    msg = got[0]
    assert msg.header.frame_id == 'laser'
    assert msg.radiation_type == Range.INFRARED
    assert msg.range == pytest.approx(1234.5)
    assert msg.min_range == pytest.approx(1.0)
    assert msg.max_range == pytest.approx(3000.0)
    assert msg.field_of_view == pytest.approx(0.01)  # LRF3000A1 table value


def test_below_minimum_is_negative_infinity():
    node, _ = make_node(raw=3)  # 0.3 m, below the 1.0 m minimum
    try:
        msg = collect(node)[0]
    finally:
        node.destroy_node()
    assert math.isinf(msg.range) and msg.range < 0


def test_failed_measurement_is_nan():
    node, _ = make_node(raw=0, status=0x00)
    try:
        msg = collect(node)[0]
    finally:
        node.destroy_node()
    assert math.isnan(msg.range)


def test_continuous_mode_streams_frames():
    node, port = make_node(raw=5000, extra=[
        Parameter('continuous', value=True),
        Parameter('acknowledge_protocol_hold', value=True)])
    try:
        msg = collect(node, count=2)[0]
    finally:
        node.destroy_node()
    assert port.closed
    assert msg.range == pytest.approx(500.0)


def test_model_without_documented_scale_is_refused():
    with pytest.raises(RuntimeError):
        ErdiLrfNode(serial_factory=lambda *a: None, parameter_overrides=[
            Parameter('model', value='SPD1200D03'),
            Parameter('baud', value=115200)])
