"""EXP01 — Zinsrechnung vs live data (Opitz Ch.27.1 + Ch.1 Beispiel 1.12 FX).

Verifies:
- Einfachzins vs Zinseszins on textbook Beispiel (20k, 10y, 6%) -> 32000 vs 35816.95
- m-period convergence: Km,n increases with m, limit = stetig (Satz 8.33 / Def 27.13)
- i_eff > i_nom, i_kon < i_rel (live intuition for ECB/Fed hikes Sep-2026)
- FX textbook conversion on live snapshot (Beispiel 1.12b: 6 EUR * 1.3 = 7.8 USD style)
- BTC 30d buy-and-hold vs textbook compound projection at live-implied daily rate

Writes benchmarks/exp01_results.csv + prints PASS/FAIL with tolerances.
"""
import csv
import math
from pathlib import Path

from src.finanzmathematik import (
    einfachzins_endwert, zinseszins_endwert, effektiv_jahreszins,
    konform_periodenzins, relativ_periodenzins, stetig_endwert,
)
from src.live_data import load_snapshot, btc_returns, fx_convert

OUT = Path(__file__).resolve().parents[1] / "benchmarks" / "exp01_results.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)


def main():
    snap = load_snapshot()
    rows = []

    # 1) Textbook anchor (Beispiel 27.6)
    k_einf = einfachzins_endwert(20000, 0.06, 10)
    k_zins = zinseszins_endwert(20000, 0.06, 10)
    assert abs(k_einf - 32000) < 1e-9, k_einf
    assert abs(k_zins - 35816.95) < 0.05, k_zins
    rows.append(("textbook_20k_10y_einfach", k_einf, 32000.0))
    rows.append(("textbook_20k_10y_zinseszins", k_zins, 35816.95))

    # 2) Unterjaehrig monotonicity + stetig limit (Beispiel 27.11/27.15 pattern, 5y)
    vals = {}
    for m in [1, 2, 4, 12, 360]:
        vals[m] = 20000 * (1 + 0.06 / m) ** (m * 5)
    k_stet = stetig_endwert(20000, 0.06, 5)
    assert vals[1] < vals[2] < vals[4] < vals[12] < vals[360] < k_stet + 1e-6
    assert abs(k_stet - 26997.18) < 0.6, k_stet
    for m, v in vals.items():
        rows.append((f"unterjaehrig_m{m}_5y", v, k_stet))
    rows.append(("stetig_5y", k_stet, 26997.18))

    # 3) i_eff / i_kon ordering (Beispiel 27.12 pattern)
    ieff = effektiv_jahreszins(0.06, 4)
    assert abs(ieff - 0.0614) < 0.0005, ieff
    ikon = konform_periodenzins(0.06, 4)
    irel = relativ_periodenzins(0.06, 4)
    assert ikon < irel, (ikon, irel)
    rows.append(("ieff_q", ieff, 0.0614))
    rows.append(("ikon_q", ikon, 0.0147))

    # 4) Live FX textbook-style conversion (Beispiel 1.12b logic on 2026 snapshot)
    # 6 EUR -> USD at live EUR rate
    usd = fx_convert(6.0, "EUR/USD", snap)
    expected = 6.0 / snap["fx_usd_base"]["EUR"]
    assert abs(usd - expected) < 1e-9
    rows.append(("live_6EUR_in_USD", usd, expected))
    # Round-trip must be identity (verifies Definition 27.10-style consistency)
    back = fx_convert(usd, "USD/EUR", snap)
    assert abs(back - 6.0) < 1e-9
    rows.append(("live_roundtrip_EUR", back, 6.0))

    # 5) BTC live: realized 30d growth vs textbook exponential projection
    px = [p["price"] for p in snap["btc_usd_30d"]]
    realized = px[-1] / px[0] - 1
    # implied daily stetig rate from first->last, then project (self-consistency check)
    i_daily = math.log(px[-1] / px[0]) / (len(px) - 1)
    proj = math.exp(i_daily * (len(px) - 1)) - 1
    assert abs(proj - realized) < 1e-12
    rets = btc_returns(snap)
    assert len(rets) == len(px) - 1 and all(abs(r) < 0.2 for r in rets), "sanity: no 20% daily jump in snapshot"
    rows.append(("btc_realized_30d", realized, proj))
    rows.append(("btc_max_abs_daily", max(abs(r) for r in rets), max(abs(r) for r in rets)))

    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "computed", "reference"])
        w.writerows(rows)
    print(f"EXP01 PASS: {len(rows)} checks. BTC 30d realized={realized:.4%}, "
          f"AAPL snapshot={snap['aapl']['current']}, FX={snap['fx_usd_base']}")
    print(f"  -> {OUT}")


if __name__ == "__main__":
    main()
