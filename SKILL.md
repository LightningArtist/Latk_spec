---
name: latk
description: Command-line operations on Lightning Artist Toolkit (Latk) 3D brushstroke files, organized by operation and implementation language. Use when converting, normalizing, or batch-processing .latk/.json/.tilt files, e.g. batch converting Tilt Brush / Open Brush .tilt sketches into normalized .latk files.
---

# Latk CLI Operations

Scripted, repeatable operations on Latk files. For the file format itself and the per-language libraries, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Conventions

These apply to every operation below.

- **Containers:** a `.latk` file is a zip holding one `<stem>.json`. A `.json` file is the same document uncompressed. All Latk readers accept either.
- **Axes:** Latk files on disk are Y-up. latkpy holds data Z-up in memory (Blender convention) and swaps axes on `read()`/`write()` by default. Leave the `yUp` arguments at their defaults so the round trip stays consistent.
- **Normalized:** points are uniformly scaled so the drawing's largest bounding-box extent is exactly 1, with the bounding-box minimum at the origin. Aspect ratio is preserved, so every coordinate falls in `[0, 1]`.
- **Batch behavior:** scripts print one line per file (`ok:`, `skip (exists):`, or `FAIL:` on stderr), end with a summary line, skip existing outputs unless `--force` is given, and exit `1` if any file failed.

## Operations

| Operation | Python | JavaScript | C++ | Java | C# |
|---|---|---|---|---|---|
| [Tilt → normalized Latk](#1-tilt--normalized-latk) | [`scripts/python/tilt_to_latk.py`](scripts/python/tilt_to_latk.py) | — | — | — | — |

---

## 1. Tilt → normalized Latk

Converts Tilt Brush / Open Brush binary `.tilt` sketches into normalized `.latk` files.

### Python

**Requires:** Python 3 and the latk library (`pip install latk`; verified with latk 2.9.2 and NumPy 2.x).

```bash
# Every .tilt under a folder (recursive), mirroring subfolders into out/
python3 scripts/python/tilt_to_latk.py path/to/sketches -o out/

# Specific files; output goes next to each input when -o is omitted
python3 scripts/python/tilt_to_latk.py a.tilt b.tilt

# Uncompressed .json for inspection, overwriting earlier output
python3 scripts/python/tilt_to_latk.py path/to/sketches -o out/ --json --force
```

| Argument | Meaning |
|---|---|
| `INPUT ...` | `.tilt` files and/or directories (searched recursively, case-insensitive `.tilt`) |
| `-o, --out-dir DIR` | Output root. Subfolders relative to each input directory are mirrored. Default: next to each input |
| `--json` | Write uncompressed `.json` instead of zipped `.latk` |
| `--force` | Overwrite existing outputs (otherwise they are skipped) |

**Per file, the script:**

1. Reads the sketch with `Latk().readTiltBrush(path)`, producing one layer named `TiltBrush` with one frame. Each Tilt stroke becomes a `LatkStroke` with its RGB brush color, and each control point becomes a `LatkPoint` whose pressure comes from the control point's first extension.
2. Normalizes all points (see [Conventions](#conventions)). Any NaN pressure or strength is set to `1.0`.
3. Writes Latk 2.9 JSON with `Latk.write(..., zipped=False)`, then zips it as `<stem>.json` inside `<stem>.latk`.

**Verify an output:**

```bash
python3 -c "from latk import Latk; import sys; la = Latk(sys.argv[1]); print(la.countAllStrokes(), 'strokes', la.countAllPoints(), 'points')" out/sketch.latk
```

**latkpy caveats this script works around.** Keep these in mind when calling the library directly:

- `Latk.normalize()` is **not** used. It scales by `max(all axis maxima) − min(all axis minima)` rather than the largest extent, so the result depends on where the drawing sits in space. A stroke 1 unit long lands at 1.0, 0.19, or 0.02 for Z offsets of 0, 5, and 50.
- `Latk.write(zipped=True)` names the zip entry after the full output path (e.g. `/Users/…/out.json`), which is why the script zips the JSON itself.
- `readTiltBrush` handles binary `.tilt` only. Its Tilt Brush JSON-export branch is broken (latkpy `ISSUES.md` #1, #2). Non-zip input fails with `BadZipFile`.
- `readTiltBrush` scales positions by 0.1 and swaps Y/Z. Normalization makes the scale irrelevant.
- Brush names and per-point vertex colors are not carried over, because latkpy's Tilt reader does not extract them.
- No point reduction is applied. If you add `Latk.clean()` afterwards, note that it resets `vertex_color` (latkpy `ISSUES.md` #17). That is harmless for Tilt imports, which have no vertex colors.

---

## Adding an operation

1. Put the implementation in `scripts/<language>/<operation>` (e.g. `scripts/javascript/tilt_to_latk.mjs`).
2. Add a row (or fill a cell) in the [Operations](#operations) table.
3. Add a numbered section with one `###` subsection per language covering requirements, usage, behavior, and library caveats. Follow the [Conventions](#conventions) for output and normalization so results match across languages.
4. Test on real files before documenting. The latkpy repo ships `example/sketch.tilt` (161 strokes) and `example/latk_logo.latk` (160 strokes).
