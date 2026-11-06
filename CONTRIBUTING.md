# Contributing

Thanks for helping improve `erdi_lrf_ros2`.

Any contribution that you make to this repository will
be under the MIT license, as dictated by that
[license](https://opensource.org/licenses/MIT).

* Open an issue first for larger changes. Then fork, create a branch, and open a pull request against `main`.
* Keep changes focused, add or update tests, and update `CHANGELOG.rst` for user-visible changes.
* Run the tests before pushing (ROS 2 Jazzy or Humble):

```bash
cd ~/ros2_ws
colcon build --packages-select erdi_lrf_ros2
colcon test --packages-select erdi_lrf_ros2 --event-handlers console_direct+
colcon test-result --verbose
```

CI runs the same commands in `ros:jazzy` and `ros:humble` containers.
