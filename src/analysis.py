"""Analysis helpers: Folgen/Reihen (Ch.8), Euler e as limit, hidden-pattern stats."""
from __future__ import annotations

import math


def euler_folge(n: int) -> float:
    return (1.0 + 1.0 / n) ** n


def euler_reihe(n: int) -> float:
    return sum(1.0 / math.factorial(i) for i in range(n + 1))


def geometrische_reihe_sum(b0: float, q: float, n: int) -> float:
    if q == 1:
        return b0 * (n + 1)
    return b0 * (1 - q ** (n + 1)) / (1 - q)


def integer_gap(lp_value: float, ilp_value: float) -> float:
    """Relative integrality gap — textbook rounding-failure metric (cf. Beispiel 30.2)."""
    if lp_value == 0:
        return 0.0
    return abs(lp_value - ilp_value) / abs(lp_value)


def max_drawdown(prices: list[float]) -> float:
    peak, mdd = prices[0], 0.0
    for p in prices[1:]:
        peak = max(peak, p)
        mdd = max(mdd, (peak - p) / peak)
    return mdd


def sharpe_like(returns: list[float]) -> float:
    import statistics
    if len(returns) < 2:
        return 0.0
    mu = statistics.fmean(returns)
    sd = statistics.pstdev(returns)
    return mu / sd if sd else 0.0
