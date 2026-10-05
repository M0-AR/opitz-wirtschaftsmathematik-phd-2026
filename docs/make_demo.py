"""Generate reproducible demo assets: demo.gif (inline in README) + demo.mp4 (Pages embed).

Re-runnable: python3 docs/make_demo.py
Requires: matplotlib + ffmpeg (verified in CI via `which ffmpeg`).
"""
import pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def main():
    # Data: compounding convergence frames
    ms = np.array([1, 2, 4, 12, 52, 360])
    vals = np.array([20000 * (1 + 0.06 / m) ** (m * 5) for m in ms])
    stet = 20000 * np.exp(0.06 * 5)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.set_xscale("log")
    ax.set_xlabel("m (log)")
    ax.set_ylabel("20000 after 5y at 6%")
    ax.set_title("Demo: discrete compounding -> continuous limit")
    ax.axhline(stet, linestyle="--", alpha=0.5)
    line, = ax.plot([], [], marker="o")
    txt = ax.text(0.05, 0.9, "", transform=ax.transAxes)
    ax.set_xlim(0.9, 400)
    ax.set_ylim(vals.min() - 20, stet + 20)

    def init():
        line.set_data([], [])
        return line, txt

    def update(i):
        x = ms[: i + 1]
        y = vals[: i + 1]
        line.set_data(x, y)
        txt.set_text(f"m={ms[i]} value={vals[i]:.2f}")
        return line, txt

    ani = animation.FuncAnimation(fig, update, frames=len(ms), init_func=init, interval=600)
    gif_path = DOCS / "demo.gif"
    mp4_path = DOCS / "demo.mp4"
    ani.save(gif_path, writer="pillow", fps=2)
    try:
        ani.save(mp4_path, writer="ffmpeg", fps=2, dpi=150)
    except Exception as e:
        print("mp4 skipped:", e)
    plt.close(fig)
    print("DEMO_OK", gif_path.exists(), mp4_path.exists(),
          gif_path.stat().st_size, mp4_path.stat().st_size if mp4_path.exists() else 0)


if __name__ == "__main__":
    main()
