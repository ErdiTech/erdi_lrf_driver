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

"""Validate the per-model beam divergence table."""

from erdi_lrf_ros2._erdi_lrf.models import (
    FIELD_OF_VIEW_RAD, field_of_view_rad, MODELS)


def test_every_tabulated_model_exists_and_fov_is_sane():
    assert FIELD_OF_VIEW_RAD
    for model, fov in FIELD_OF_VIEW_RAD.items():
        assert model in MODELS, model
        assert 0.0 < fov < 0.1, (model, fov)


def test_lookup_and_fallback():
    assert field_of_view_rad('lr2000e2') == 0.006
    assert field_of_view_rad('LRF50H') == 0.002
    assert field_of_view_rad('LRF50H', default=0.005) == 0.005
