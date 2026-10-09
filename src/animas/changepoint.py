"""Change-point search that does not know the release date.

Both methods use a mean-shift (L2) cost on a regularly indexed monthly series and the
same penalty; `pelt` is exact for that cost and `binary_segmentation` returns the same
kind of answer greedily, with the first split being the single strongest change-point.
The penalty is beta * sigma^2 * log(n) with sigma^2 from the median absolute
first difference (robust to the shifts being searched for).
"""

from __future__ import annotations

import numpy as np

MIN_SEGMENT = 12  # months


def robust_sigma2(x: np.ndarray) -> float:
    d = np.diff(x)
    mad = np.median(np.abs(d - np.median(d)))
    return float((1.4826 * mad) ** 2 / 2.0) if mad > 0 else float(np.var(x))


def _segment_cost(cs: np.ndarray, cs2: np.ndarray, a: int, b: int) -> float:
    """Sum of squared deviations from the segment mean for x[a:b]."""
    n = b - a
    s = cs[b] - cs[a]
    return float(cs2[b] - cs2[a] - s * s / n)


def pelt(x: np.ndarray, *, penalty: float | None = None, beta: float = 3.0,
         min_segment: int = MIN_SEGMENT) -> list[int]:
    """Exact minimiser of sum(segment costs) + penalty * (number of change-points).

    Returns the start indices of new segments (a change-point at index k means the mean
    changes between x[k-1] and x[k]).
    """
    x = np.asarray(x, dtype=float)
    n = len(x)
    if penalty is None:
        penalty = beta * robust_sigma2(x) * np.log(n)
    cs = np.concatenate([[0.0], np.cumsum(x)])
    cs2 = np.concatenate([[0.0], np.cumsum(x * x)])
    F = np.full(n + 1, np.inf)
    F[0] = -penalty
    last = np.zeros(n + 1, dtype=int)
    cands = [0]
    for t in range(min_segment, n + 1):
        best, arg = np.inf, 0
        for s in cands:
            if t - s < min_segment:
                continue
            v = F[s] + _segment_cost(cs, cs2, s, t) + penalty
            if v < best:
                best, arg = v, s
        F[t], last[t] = best, arg
        # pruning: drop candidates that can never win again
        cands = [s for s in cands if F[s] + _segment_cost(cs, cs2, s, t) <= F[t]] + [t]
    cps = []
    t = n
    while last[t] > 0:
        cps.append(int(last[t]))
        t = last[t]
    return sorted(cps)


def binary_segmentation(x: np.ndarray, *, penalty: float | None = None, beta: float = 3.0,
                        min_segment: int = MIN_SEGMENT, max_cps: int = 5) -> list[tuple[int, float]]:
    """Greedy splits; returns [(index, cost reduction)] in the order found (strongest first)."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    if penalty is None:
        penalty = beta * robust_sigma2(x) * np.log(n)
    cs = np.concatenate([[0.0], np.cumsum(x)])
    cs2 = np.concatenate([[0.0], np.cumsum(x * x)])
    segments = [(0, n)]
    found: list[tuple[int, float]] = []
    while len(found) < max_cps:
        best = None
        for a, b in segments:
            base = _segment_cost(cs, cs2, a, b)
            for k in range(a + min_segment, b - min_segment + 1):
                gain = base - _segment_cost(cs, cs2, a, k) - _segment_cost(cs, cs2, k, b)
                if best is None or gain > best[1]:
                    best = (k, gain, (a, b))
        if best is None or best[1] <= penalty:
            break
        k, gain, (a, b) = best
        found.append((int(k), float(gain)))
        segments.remove((a, b))
        segments += [(a, k), (k, b)]
    return found
