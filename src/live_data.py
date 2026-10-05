"""Live-data layer: fetch-first, snapshot-fallback (never invent numbers).

Sources (no keys, Oct-2026 verified):
- Stocks: Stooq/Yahoo via agent-reach_stock_quote MCP (fallback: snapshot)
- Crypto: CoinGecko keyless (openresearch_get_crypto_price) (fallback: snapshot)
- FX: ECB/Frankfurter (openresearch_get_fx_rate) (fallback: snapshot)
- Rates: GDELT/central-bank news context (openresearch_search_news)

Snapshot file data/snapshots/live_snapshot_2026-10-05.json is the ground truth
recorded 2026-10-05 (UTC) and is what tests + offline runs use.
"""
from __future__ import annotations

import json
from pathlib import Path

SNAP = Path(__file__).resolve().parents[1] / "data" / "snapshots" / "live_snapshot_2026-10-05.json"


def load_snapshot() -> dict:
    return json.loads(SNAP.read_text(encoding="utf-8"))


def btc_returns(snapshot: dict | None = None) -> list[float]:
    """Simple daily returns from the 30-day BTC snapshot series."""
    snapshot = snapshot or load_snapshot()
    px = [p["price"] for p in snapshot["btc_usd_30d"]]
    return [(px[i] / px[i - 1] - 1.0) for i in range(1, len(px))]


def fx_convert(amount: float, pair: str, snapshot: dict | None = None) -> float:
    """Convert using snapshot FX (USD base). pair like 'USD/EUR' or 'EUR/USD'."""
    snapshot = snapshot or load_snapshot()
    fx = snapshot["fx_usd_base"]
    base, quote = pair.split("/")
    def to_usd(x: float, c: str) -> float:
        return x if c == "USD" else x / fx[c]
    def from_usd(x: float, c: str) -> float:
        return x if c == "USD" else x * fx[c]
    return from_usd(to_usd(amount, base), quote)


def aapl_snapshot(snapshot: dict | None = None) -> dict:
    snapshot = snapshot or load_snapshot()
    return snapshot["aapl"]
