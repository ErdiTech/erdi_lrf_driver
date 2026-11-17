^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package erdi_lrf_driver
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

0.3.0 (2026-11-18)
------------------
* Vendored codec refreshed from ``erdi-lrf`` 0.1.8: adds ``LRF10VB`` and
  ``SPD1200S2G`` (24 models in total). ``tools/sync_codec.py`` mirrors the
  library byte-for-byte and a test fails if the copy drifts from an installed
  ``erdi-lrf``.
* Beam-divergence table moved out of the vendored codec into
  ``erdi_lrf_driver.fov``.
* Contributors: ERDI TECH LTD

0.2.0 (2026-11-11)
------------------
* Rename package ``erdi_lrf_ros2`` to ``erdi_lrf_driver`` (REP-144: no redundant
  ``ros2``, driver packages end in ``driver``). Topics, parameters and
  executable names are unchanged.
* Contributors: ERDI TECH LTD

0.1.0 (2026-11-06)
------------------
* Initial release: ``erdi_lrf_node`` publishing ``sensor_msgs/msg/Range`` for
  ERDI UART laser rangefinder modules (protocol families A and B).
* Bundled serial codec (from ``erdi-lrf`` 0.1.1) so the package depends only
  on rosdep-resolvable keys (``python3-serial``).
* Per-model beam divergence table (``field_of_view`` 0.0 = use table); ``continuous`` and ``acknowledge_protocol_hold`` parameters; ``range_node`` executable alias.
* Contributors: ERDI Technology
