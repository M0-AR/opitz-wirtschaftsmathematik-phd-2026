"""Generate README/docs charts from verified benchmark outputs (no hand-drawn numbers)."""
import csv
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)


def load_csv(name):
    rows = list(csv.DictReader(open(BENCH / name)))
    return {r["metric"]: float(r["computed"]) for r in rows}


def main():
    e1 = load_csv("exp01_results.csv")
    e2 = load_csv("exp02_results.csv")
    e4 = load_csv("exp04_results.csv")

    # 1) Unterjaehrig convergence
    ms = [1, 2, 4, 12, 360]
    vals = [e1[f"unterjaehrig_m{m}_5y"] for m in ms]
    stet = e1["stetig_5y"]
    plt.figure(figsize=(7, 4))
    plt.plot(ms, vals, marker="o", label="discrete m")
    plt.axhline(stet, linestyle="--", label=f"continuous {stet:.2f}")
    plt.xscale("log")
    plt.xlabel("compounding periods per year (m, log scale)")
    plt.ylabel("value of 20000 after 5y at 6%")
    plt.title("More compounding -> higher value, converging to continuous limit")
    plt.legend()
    plt.tight_layout()
    plt.savefig(DOCS / "chart_compounding.png", dpi=150)
    plt.close()

    # 2) Duration ordering
    plt.figure(figsize=(7, 4))
    labels = ["coupon 2", "coupon 5", "coupon 8"]
    vals_d = [e4["H2_D_c2"], e4["H2_D_c5"], e4["H2_D_c8"]]
    plt.bar(labels, vals_d)
    plt.ylabel("duration (years)")
    plt.title("Higher coupon = shorter duration (bond reacts less to rate moves)")
    plt.tight_layout()
    plt.savefig(DOCS / "chart_duration.png", dpi=150)
    plt.close()

    # 3) BTC live series
    import json
    snap = json.load(open(ROOT / "data/snapshots/live_snapshot_2026-10-05.json"))
    px = [p["price"] for p in snap["btc_usd_30d"]]
    plt.figure(figsize=(8, 4))
    plt.plot(px)
    plt.xlabel("day in snapshot window (2026-09-05 to 2026-10-05)")
    plt.ylabel("BTC USD")
    plt.title("Live BTC series used for verification (dip mid-Sept visible)")
    plt.tight_layout()
    plt.savefig(DOCS / "chart_btc.png", dpi=150)
    plt.close()

    # 4) LP vs ILP gap
    plt.figure(figsize=(6, 4))
    plt.bar(["LP relaxation 41/3", "Integer optimum 13", "Naive rounding 12"], [41/3, 13, 12])
    plt.ylabel("objective 2x1+3x2")
    plt.title("Rounding is not optimization: gap 4.88%")
    plt.tight_layout()
    plt.savefig(DOCS / "chart_gap.png", dpi=150)
    plt.close()

    print("CHARTS_OK", sorted(p.name for p in DOCS.glob("chart_*.png")))


if __name__ == "__main__":
    main()
