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

"""Per-model beam divergence for ``sensor_msgs/msg/Range.field_of_view``."""

from typing import Mapping


#: Full beam divergence in radians, parsed from the published specification
#: table of each model at https://erdilrf.com/models/ (2026-11-06).  Values are
#: the datasheet *upper bound* ("< 6 mrad" -> 0.006).  Models absent from this
#: table have no divergence row in their published specification.
FIELD_OF_VIEW_RAD: Mapping[str, float] = {
    'LR1000E2': 0.009,  # < 9 mrad
    'LR1000E4': 0.009,  # < 9 mrad
    'LR1200E2': 0.004,  # < 4 mrad (small laser spot)
    'LR1200E4': 0.004,  # < 4 mrad (small laser spot)
    'LR1500E2': 0.006,  # < 6 mrad (small laser spot)
    'LR1500E4': 0.006,  # < 6 mrad (small laser spot)
    'LR2000E2': 0.006,  # < 6 mrad
    'LR2000E4': 0.006,  # < 6 mrad
    'LRF3000A1': 0.01,  # ≤10 mrad
    'SPD1200N0': 0.0045,  # <4.5 mrad
    'SPD1200N2': 0.0045,  # <4.5 mrad
    'SPD1200N4': 0.0045,  # <4.5 mrad
}


def field_of_view_rad(model: str, default: float = 0.002) -> float:
    """Return the tabulated beam divergence (rad) for ``model``, else ``default``."""
    return FIELD_OF_VIEW_RAD.get(model.upper(), default)
