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

"""The vendored codec must match the erdi-lrf library and cover its models."""

import importlib.util
import pathlib

from erdi_lrf_driver import _erdi_lrf
from erdi_lrf_driver._erdi_lrf.models import MODELS
from erdi_lrf_driver.fov import FIELD_OF_VIEW_RAD
import pytest


def test_vendored_version_and_new_models():
    assert _erdi_lrf.__version__ >= '0.1.8'
    assert 'LRF10VB' in MODELS
    assert 'SPD1200S2G' in MODELS


def test_every_fov_entry_is_a_known_model():
    assert set(FIELD_OF_VIEW_RAD) <= set(MODELS)


def test_vendored_files_match_installed_erdi_lrf():
    """When ``pip install erdi-lrf`` is present, the mirror must be identical."""
    spec = importlib.util.find_spec('erdi_lrf')
    if spec is None or not spec.submodule_search_locations:
        pytest.skip('erdi-lrf library not installed')
    lib = pathlib.Path(list(spec.submodule_search_locations)[0])
    here = pathlib.Path(_erdi_lrf.__file__).parent
    for name in ('device.py', 'errors.py', 'models.py',
                 'protocol_a.py', 'protocol_b.py'):
        a = (lib / name).read_bytes().replace(b'\r\n', b'\n')
        b = (here / name).read_bytes().replace(b'\r\n', b'\n')
        assert a == b, f'{name} drifted from erdi-lrf; run tools/sync_codec.py'
