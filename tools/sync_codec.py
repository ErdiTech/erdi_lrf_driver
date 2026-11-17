#!/usr/bin/env python3
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

"""
Refresh the vendored serial codec from the ``erdi-lrf`` Python library.

ROS packages released to the official index may only depend on rosdep keys, and
``erdi-lrf`` is a PyPI package, so the codec is vendored byte-for-byte (LF line
endings) into ``erdi_lrf_driver/_erdi_lrf``.  Everything ROS-specific lives
outside that folder, so this copy is always a plain mirror of the library.

Usage::

    python3 tools/sync_codec.py /path/to/erdi-lrf-drivers/python/erdi_lrf
    python3 tools/sync_codec.py --check /path/to/erdi_lrf   # exit 1 on drift
"""
import argparse
import pathlib
import sys

FILES = ('__init__.py', 'device.py', 'errors.py', 'models.py',
         'protocol_a.py', 'protocol_b.py')
DEST = pathlib.Path(__file__).resolve().parent.parent / \
    'erdi_lrf_driver' / '_erdi_lrf'


def _read(path):
    return path.read_bytes().replace(b'\r\n', b'\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source', type=pathlib.Path)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    drift = []
    for name in FILES:
        src = _read(args.source / name)
        dst = DEST / name
        if dst.exists() and _read(dst) == src:
            continue
        drift.append(name)
        if not args.check:
            dst.write_bytes(src)
    if drift:
        print(('DRIFT: ' if args.check else 'updated: ') + ', '.join(drift))
    else:
        print('vendored codec identical to library')
    return 1 if (args.check and drift) else 0


if __name__ == '__main__':
    sys.exit(main())
