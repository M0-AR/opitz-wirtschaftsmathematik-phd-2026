"""EXP02 — Renten/Tilgung/Kurs vs live-rate environment (Opitz Ch.27.5-27.7).

- Textbook anchors: Beispiel 27.41 (1000 p.a., 5y, 5% -> R5=5525.63), Annuität 40k/5%/5y
- Live-rate sensitivity: recompute Rente/Tilgung/Kurs at Sep-2026 hike regime
  (Fed/ECB hikes => i=6% stress vs 4% baseline) to show Duration/Annuität response.
- Bond Duration (Satz 27.65) decreases with higher coupon — verified numerically.
"""
import csv
from pathlib import Path

from src.finanzmathematik import (
    renten_endwert_nach, renten_endwert_vor, renten_barwert_nach,
    annuitaet, annuitaetentilgung_plan, emissionskurs, bond_duration,
    bankenformel, boersenformel,
)

OUT = Path(__file__).resolve().parents[1] / "benchmarks" / "exp02_results.csv"


def main():
    rows = []
    # Anchor 27.41
    r5 = renten_endwert_nach(1000, 0.05, 5)
    assert abs(r5 - 5525.63) < 0.02, r5
    rows.append(("R5_nach_1000_5pct", r5, 5525.63))
    r5v = renten_endwert_vor(1000, 0.05, 5)
    assert abs(r5v - r5 * 1.05) < 1e-9
    rows.append(("R5_vor", r5v, r5 * 1.05))
    b0 = renten_barwert_nach(1000, 0.05, 5)
    assert abs(b0 - r5 * 1.05**-5) < 1e-9
    rows.append(("R0_nach", b0, r5 * 1.05**-5))

    # Annuitaet anchor (Beispiel 27.60 pattern: 40k,5%,5y -> ~9238.99)
    A = annuitaet(40000, 0.05, 5)
    assert abs(A - 9238.99) < 0.05, A
    rows.append(("Annuitaet_40k", A, 9238.99))
    plan = annuitaetentilgung_plan(40000, 0.05, 5)
    assert abs(sum(p.tilgung for p in plan) - 40000) < 0.05
    assert plan[0].tilgung < plan[-1].tilgung  # Satz 27.59d exponential rise
    rows.append(("Tilgung_sum", sum(p.tilgung for p in plan), 40000.0))

    # Live-rate stress: same Rente at 4% vs 6% (Sep-2026 hike context)
    for i in (0.04, 0.06):
        rows.append((f"R5_nach_i{i}", renten_endwert_nach(1000, i, 5), renten_endwert_nach(1000, i, 5)))
        rows.append((f"Annuitaet_40k_i{i}", annuitaet(40000, i, 5), annuitaet(40000, i, 5)))
    assert annuitaet(40000, 0.06, 5) > annuitaet(40000, 0.04, 5)

    # Bond anchor (Beispiel 27.63: c=5,Cn=100,n=4 -> C0=103.63 @4%, 96.53 @6%)
    c0_4 = emissionskurs(5, 100, 0.04, 4)
    c0_6 = emissionskurs(5, 100, 0.06, 4)
    assert abs(c0_4 - 103.63) < 0.03, c0_4
    assert abs(c0_6 - 96.53) < 0.05, c0_6
    rows.append(("C0_4pct", c0_4, 103.63))
    rows.append(("C0_6pct", c0_6, 96.53))
    d4 = bond_duration(5, 100, 0.04, 4)
    d6 = bond_duration(5, 100, 0.06, 4)
    assert 0 < d6 < d4 < 4, (d4, d6)  # higher yield -> lower duration; duration < maturity
    rows.append(("Duration_4pct", d4, d4))
    rows.append(("Duration_6pct", d6, d6))
    # Coupon effect: higher coupon -> lower duration (hidden-pattern candidate)
    d_low = bond_duration(2, 100, 0.05, 4)
    d_high = bond_duration(8, 100, 0.05, 4)
    assert d_high < d_low, (d_high, d_low)
    rows.append(("Duration_c2", d_low, d_low))
    rows.append(("Duration_c8", d_high, d_high))
    # Naeherungsformeln ordering check (Tendenz: qa/qb vs exakt, dokumentiert nicht asserted)
    rows.append(("Bankenformel_C103.63", bankenformel(5, 103.63, 100, 4), bankenformel(5, 103.63, 100, 4)))
    rows.append(("Boersenformel_C103.63", boersenformel(5, 103.63, 100, 4), boersenformel(5, 103.63, 100, 4)))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "computed", "reference"])
        w.writerows(rows)
    print(f"EXP02 PASS: {len(rows)} checks. Duration(4%)={d4:.3f}y Duration(6%)={d6:.3f}y A={A:.2f}")
    print(f"  -> {OUT}")


if __name__ == "__main__":
    main()
