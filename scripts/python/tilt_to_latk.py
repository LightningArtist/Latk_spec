#!/usr/bin/env python3
"""Batch convert Tilt Brush / Open Brush .tilt files into normalized Latk files.

Uses the latk Python library (pip install latk) to parse .tilt files and write
Latk JSON. Each drawing is uniformly scaled so its largest dimension spans 0-1,
with its bounding box minimum at the origin (aspect ratio preserved).

Usage:
    python3 tilt_to_latk.py INPUT [INPUT ...] [-o OUT_DIR] [--json] [--force]

INPUT may be a .tilt file or a directory (searched recursively for *.tilt).
"""

import argparse
import math
import os
import sys
import tempfile
import zipfile

import numpy as np
from latk import Latk


def find_tilt_files(inputs):
    """Yield (path, root) pairs; root is the directory the input was found under."""
    for item in inputs:
        if os.path.isdir(item):
            for dirpath, _, filenames in os.walk(item):
                for name in sorted(filenames):
                    if name.lower().endswith(".tilt"):
                        yield os.path.join(dirpath, name), item
        elif os.path.isfile(item):
            yield item, os.path.dirname(item)
        else:
            print("not found: " + item, file=sys.stderr)


def normalize(la):
    """Uniformly scale all points so the largest extent spans 0-1, min corner at origin.

    Latk.normalize() is not used: it divides by max(all maxes) - min(all mins)
    across axes, so its output scale depends on where the drawing sits in space.
    """
    points = [pt for layer in la.layers for frame in layer.frames
              for stroke in frame.strokes for pt in stroke.points]
    if not points:
        raise ValueError("no points")
    coords = np.array([pt.co for pt in points], dtype=np.float64)
    mins = coords.min(axis=0)
    extent = (coords.max(axis=0) - mins).max()
    if not extent > 0:
        raise ValueError("degenerate drawing (all points coincide)")
    coords = (coords - mins) / extent
    for pt, co in zip(points, coords):
        pt.co = tuple(co.tolist())
        # Latk.write emits NaN unquoted, which strict JSON readers reject.
        if math.isnan(pt.pressure):
            pt.pressure = 1.0
        if math.isnan(pt.strength):
            pt.strength = 1.0


def write_latk(la, out_path, as_json):
    if as_json:
        la.write(out_path, zipped=False)
        return
    # Latk.write(zipped=True) names the zip entry after the full output path,
    # so write plain JSON and zip it under its basename instead.
    stem = os.path.splitext(os.path.basename(out_path))[0]
    with tempfile.TemporaryDirectory() as tmp:
        json_path = os.path.join(tmp, stem + ".json")
        la.write(json_path, zipped=False)
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(json_path, stem + ".json")


def main():
    parser = argparse.ArgumentParser(description="Batch convert .tilt files to normalized .latk files.")
    parser.add_argument("inputs", nargs="+", help=".tilt files or directories to search recursively")
    parser.add_argument("-o", "--out-dir", help="output directory, mirroring input subfolders (default: next to each input)")
    parser.add_argument("--json", action="store_true", help="write uncompressed .json instead of zipped .latk")
    parser.add_argument("--force", action="store_true", help="overwrite existing output files")
    args = parser.parse_args()

    ext = ".json" if args.json else ".latk"
    converted = skipped = failed = 0

    for path, root in find_tilt_files(args.inputs):
        stem = os.path.splitext(path)[0]
        if args.out_dir:
            stem = os.path.join(args.out_dir, os.path.relpath(stem, root))
        out_path = stem + ext

        if os.path.exists(out_path) and not args.force:
            print("skip (exists): " + out_path)
            skipped += 1
            continue

        try:
            la = Latk()
            la.readTiltBrush(path)
            normalize(la)
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
            write_latk(la, out_path, args.json)
        except Exception as e:
            print("FAIL: {} ({}: {})".format(path, type(e).__name__, e), file=sys.stderr)
            failed += 1
            continue

        print("ok: {} -> {} ({} strokes, {} points)".format(
            path, out_path, la.countAllStrokes(), la.countAllPoints()))
        converted += 1

    print("converted {}, skipped {}, failed {}".format(converted, skipped, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
