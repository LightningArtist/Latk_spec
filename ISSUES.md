# Latk — Known Issues

Issues where a Latk library does not behave as this spec ([ARCHITECTURE.md](ARCHITECTURE.md)) describes. Bugs that affect only one library's internals are tracked in that library's own `ISSUES.md`.

---

## 1. `normalize()` scale depends on where the drawing sits, not on its size

**Spec:** [ARCHITECTURE.md §2.3](ARCHITECTURE.md#23-agent-guidelines-for-latk-operations) says `normalize()` scales points "into a unified 0-1 bounding box".

**Affects:**

| Library | Location | Status |
|---|---|---|
| latkpy | `latk/latk_main.py:500-510` | Verified by execution (latk 2.9.2, commit `b759176`, NumPy 2.3.5) |
| latk.js | `latk.js:967-978` | Same formula, verified by reading the code. The function currently throws before reaching it (latk.js `ISSUES.md` A3), so fixing A3 alone will expose this bug |

```python
leastValArray = [ allX[0], allY[0], allZ[0] ]                               # :500 per-axis minima
mostValArray = [ allX[len(allX)-1], allY[len(allY)-1], allZ[len(allZ)-1] ]  # :501 per-axis maxima
...
valRange = mostVal - leastVal                                               # :506
xRange = (allX[len(allX)-1] - allX[0]) / valRange                           # :508-510
```

`valRange` is the highest maximum on any axis minus the lowest minimum on any axis. Those two values can come from different axes, so `valRange` is not the largest extent. Every point is mapped to `(co - axisMin) / valRange`. That scale is uniform, so the aspect ratio is preserved and the minimum corner lands at the origin.

`valRange` is never smaller than the largest extent, and it equals the largest extent only when a single axis holds both the lowest minimum and the highest maximum. Otherwise the whole drawing shrinks by `largestExtent / valRange`. The shrink grows as the drawing moves away from the origin along one axis.

**Verified.** One stroke from `(0, 0, z)` to `(1, 0.5, z + 0.25)`, placed at different Z positions, gives a different scale each time:

| Z offset | X extent after `normalize()` | Expected |
|---|---|---|
| 0 | 1.0 | 1.0 |
| 5 | 0.1905 | 1.0 |
| 50 | 0.0199 | 1.0 |

The same thing happens with real Tilt Brush sketches imported with `readTiltBrush`. After `normalize()`, the largest dimension of each one is:

| File | Largest dimension after `normalize()` | Expected |
|---|---|---|
| `latkpy/example/sketch.tilt` | 0.976 | 1.0 |
| `latk.js/examples/files/Untitled_2.tilt` | 0.782 | 1.0 |
| `open-brush-toolkit/Python/data/sketch1.tilt` | 0.418 | 1.0 |
| `open-brush-toolkit/Python/data/0__knEJSpIJ.tilt` | 0.117 | 1.0 |

**Impact:** the spec recommends `normalize()` for mixing sources and for building datasets. Those uses are exactly where it fails. Files normalized in a batch are not on a common scale, so a small drawing far from the origin comes out smaller than the same drawing near it.

**Fix:** divide by the largest per-axis extent:

```python
xExtent = allX[len(allX)-1] - allX[0]
yExtent = allY[len(allY)-1] - allY[0]
zExtent = allZ[len(allZ)-1] - allZ[0]
valRange = max(xExtent, yExtent, zExtent)
```

The function also needs a guard for empty input and for `valRange == 0` (latkpy `ISSUES.md` #5).

**Workaround:** [`scripts/python/tilt_to_latk.py`](scripts/python/tilt_to_latk.py) does not call `Latk.normalize()`. It runs its own corrected normalization (see [SKILL.md](SKILL.md#conventions)).
