^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package erdi_lrf_ros2
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

0.1.0 (2026-11-06)
------------------
* Initial release: ``erdi_lrf_node`` publishing ``sensor_msgs/msg/Range`` for
  ERDI UART laser rangefinder modules (protocol families A and B).
* Bundled serial codec (from ``erdi-lrf`` 0.1.1) so the package depends only
  on rosdep-resolvable keys (``python3-serial``).
* Per-model beam divergence table (``field_of_view`` 0.0 = use table); ``continuous`` and ``acknowledge_protocol_hold`` parameters; ``range_node`` executable alias.
* Contributors: ERDI Technology
