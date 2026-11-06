# erdi_lrf_ros2

[![CI](https://github.com/Tommyapi/erdi_lrf_ros2/actions/workflows/ci.yml/badge.svg)](https://github.com/Tommyapi/erdi_lrf_ros2/actions/workflows/ci.yml)

ROS 2 driver for [ERDI](https://erdilrf.com) UART laser rangefinder modules
(905 nm, hundreds of metres to kilometre-class range). It publishes the
distance sensor reading as `sensor_msgs/msg/Range`, so the module can feed
`nav2`, `robot_localization`, PX4/ArduPilot companion bridges, or your own
altitude/obstacle logic.

Both published ERDI serial protocol families are supported (family A `55 AA`
command/response, family B free-running `5C` frames). The serial codec is
bundled in the package (`erdi_lrf_ros2/_erdi_lrf`, MIT, taken from the
[`erdi-lrf`](https://pypi.org/project/erdi-lrf/) 0.1.1 Python driver), so the
only runtime dependency is `pyserial` (`python3-serial`).

## Install

```bash
cd ~/ros2_ws/src
git clone https://github.com/Tommyapi/erdi_lrf_ros2.git
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -y
colcon build --packages-select erdi_lrf_ros2
source install/setup.bash
```

## Run

```bash
ros2 launch erdi_lrf_ros2 erdi_lrf.launch.py port:=/dev/ttyUSB0 model:=LRF3000A1 rate:=10.0
# or
ros2 run erdi_lrf_ros2 erdi_lrf_node --ros-args -p port:=/dev/ttyUSB0 -p model:=LRF1500H
ros2 topic echo /range
```

Add yourself to the serial group first: `sudo usermod -aG dialout $USER`.

## Parameters

| Name | Default | Description |
|---|---|---|
| `port` | `/dev/ttyUSB0` | Serial device. |
| `model` | `LRF3000A1` | Module model, e.g. `LR1200E2`, `LRF3000A1`, `SPD1200N2`, `LRF100H`, `LRF1500H`, `LRF22VB`. See the model table at [erdilrf.com/models](https://erdilrf.com/models/). |
| `baud` | `0` | `0` = the model's documented default. `SPD1200D03` has no safe default: set it explicitly. |
| `frame_id` | `erdi_lrf_link` | TF frame of the message header. |
| `rate` | `10.0` | Polling rate in Hz. |
| `timeout` | `0.5` | Serial read timeout in seconds. |
| `min_range` / `max_range` | `0.0` | Metres. `0.0` takes the value from the model table. |
| `field_of_view` | `0.0` | Full beam divergence in radians. `0.0` = use the per-model value from the table below (fallback `0.002` for models without a published divergence). |
| `continuous` | `false` | Stream continuously instead of one request per tick. |
| `acknowledge_protocol_hold` | `false` | Needed for `continuous` on `LRF1200A1` / `LRF3000A1`, whose manuals leave the continuous-reply function byte unresolved. |
| `topic` | `range` | Output topic name. |

## Beam divergence (`field_of_view`)

Parsed from each model's published specification table at
[erdilrf.com/models](https://erdilrf.com/models/) (checked 2026-11-06); the datasheet
upper bound is used (`< 6 mrad` becomes `0.006`).

| Model | `field_of_view` (rad) |
|---|---|
| LR1000E2 | 0.009 |
| LR1000E4 | 0.009 |
| LR1200E2 | 0.004 |
| LR1200E4 | 0.004 |
| LR1500E2 | 0.006 |
| LR1500E4 | 0.006 |
| LR2000E2 | 0.006 |
| LR2000E4 | 0.006 |
| LRF3000A1 | 0.01 |
| SPD1200N0 | 0.0045 |
| SPD1200N2 | 0.0045 |
| SPD1200N4 | 0.0045 |

No divergence row is published for `LRF1200A1`, `SPD1200D03`, `LRF50H`, `LRF100H`, `LRF200H`, `LRF300H`, `LRF600H`, `LRF1500H`, `LRF22VB`, `LRF50VB`; these keep the `0.002` default, so set `field_of_view` yourself for them.

## Topics

`range` (`sensor_msgs/msg/Range`, sensor-data QoS): `radiation_type` is
`INFRARED`. Out-of-range readings follow REP-117: `-inf` below the minimum
range, `+inf` beyond the maximum or when the module reports no target, `nan`
for an invalid measurement.

## Tests

```bash
colcon test --packages-select erdi_lrf_ros2 && colcon test-result --verbose
```

Includes `ament_copyright`, `ament_flake8`, `ament_pep257` and a node test
that runs against a fake serial port, so no hardware is needed.

## See also

* Worked examples and wiring notes: [Tommyapi/erdi-lrf-ros2-examples](https://github.com/Tommyapi/erdi-lrf-ros2-examples)
* Python driver and protocol documentation: [ErdiTech/erdi-lrf-drivers](https://github.com/ErdiTech/erdi-lrf-drivers)
* Model table, datasheets and contact: [erdilrf.com](https://erdilrf.com)

## Migrating from `erdi-lrf-drivers/ros2`

This repository replaces the `ros2/erdi_lrf_ros2` package that used to live in
`ErdiTech/erdi-lrf-drivers`. Same package name, same `range` topic and
parameters; it no longer needs `pip install erdi-lrf`, and the old
`range_node` executable name still works as an alias.

## Support / 打赏

If this project saved you time, you can buy the author a coffee in crypto. Thank you!
如果这个项目帮到了你，欢迎用加密货币打赏支持，谢谢！

| Network | Asset | Address |
|---|---|---|
| TRON (TRC20) | USDT | `TNGdTwE6opH6rmUyoG1JUR7FSyEb4k273R` |
| Ethereum / BNB Chain / Polygon | USDT | `0x59c43144a862b351fa1086ae842d1327c9d91613` |
| Ethereum / Arbitrum / Base | ETH | `0x59c43144a862b351fa1086ae842d1327c9d91613` |
| Bitcoin | BTC | `1RS6tWXHregLfEsiPzVUCUBuhgDg5uTSV` |
| Solana | USDT | `HZguEXfTtLChNdJTxAYCbcGscaqikz8JYrEpUhEyeVd9` |

Please send only the listed asset on the listed network — other tokens or networks may be lost.
请按表中对应的网络转对应的币种，转错币种或网络可能无法找回。

## License

MIT, see [LICENSE](LICENSE).
