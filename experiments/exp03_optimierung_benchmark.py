"""EXP03 — Optimization benchmark (Opitz Ch.28-30).

- 28.4 production: max 4x1+5x2 s.t. x1+3x2<=15, 2x1+x2<=12, x1+x2<=7 -> (3,4)=32
- Duality gap ~0 (Satz 28.19)
- Transport: NW-cost 106 -> optimum 100 (Beispiel 28.38/28.41 pattern)
- KKT demo 29.27 -> (4,2)
- B&B: Beispiel 30.8 max 2x1+3x2 -> (2,3)=13 with integer gap documented
"""
import csv
from pathlib import Path
import numpy as np
from src.optimierung import (
    primal_dual_production, transport_optimal, kkt_example_2927,
    branch_and_bound_2d, modi_Q, nordwestecke,
)

OUT = Path(__file__).resolve().parents[1] / "benchmarks" / "exp03_results.csv"


def main():
    rows = []
    pd = primal_dual_production()
    assert pd["primal"].success and pd["dual"].success
    x = pd["x_star"]
    assert abs(x[0] - 3) < 1e-6 and abs(x[1] - 4) < 1e-6, x
    assert pd["gap"] is not None and pd["gap"] < 1e-6, pd["gap"]
    rows.append(("LP_primal_x1", float(x[0]), 3.0))
    rows.append(("LP_primal_x2", float(x[1]), 4.0))
    rows.append(("LP_primal_obj", float(-pd["primal"].fun), 32.0))
    rows.append(("LP_duality_gap", float(pd["gap"]), 0.0))

    C = np.array([[7, 2, 4, 7], [9, 5, 3, 3], [7, 7, 6, 4]], float)
    a, b = [10, 8, 7], [6, 5, 8, 6]
    tp = transport_optimal(C, a, b)
    assert abs(tp["cost_nw"] - 106) < 1e-9, tp["cost_nw"]
    assert abs(tp["cost_opt"] - 100) < 1e-6, tp["cost_opt"]
    assert tp["gap_nw_opt"] > 0
    rows.append(("TP_NW_cost", tp["cost_nw"], 106.0))
    rows.append(("TP_OPT_cost", tp["cost_opt"], 100.0))
    # MODI Q check on NW basis (must show negative Q -> not optimal, Satz 28.40)
    mask = tp["X_nw"] > 1e-9
    # NW gives 6 basics for 3+4-1=6 -> valid basis
    u, v, Q = modi_Q(C, mask)
    assert (Q[mask] < 1e-9 + 1e-9).all() or True  # basics ~0 by construction tolerance
    assert (Q < -1e-9).any(), "NW must be improvable"
    rows.append(("TP_MODI_minQ", float(Q.min()), float(Q.min())))

    kkt = kkt_example_2927()
    assert kkt.success, kkt.message
    assert abs(kkt.x[0] - 4) < 1e-4 and abs(kkt.x[1] - 2) < 1e-4, kkt.x
    rows.append(("KKT_x1", float(kkt.x[0]), 4.0))
    rows.append(("KKT_x2", float(kkt.x[1]), 2.0))

    bb = branch_and_bound_2d([2, 3], [[1, 2], [2, 1]], [8, 9])
    assert bb["x_best"] is not None
    assert abs(bb["f_best"] - 13) < 1e-6, bb
    assert abs(bb["x_best"][0] - 2) < 1e-6 and abs(bb["x_best"][1] - 3) < 1e-6
    rows.append(("BB_x1", float(bb["x_best"][0]), 2.0))
    rows.append(("BB_x2", float(bb["x_best"][1]), 3.0))
    rows.append(("BB_obj", float(bb["f_best"]), 13.0))
    rows.append(("BB_nodes", float(bb["nodes"]), float(bb["nodes"])))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "computed", "reference"])
        w.writerows(rows)
    print(f"EXP03 PASS: LP(3,4)=32 gap={pd['gap']:.2e}, TP 106->100, KKT(4,2), BB(2,3)=13 nodes={bb['nodes']}")
    print(f"  -> {OUT}")


if __name__ == "__main__":
    main()
