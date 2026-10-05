# PhD Paper Outline (companion to README)

Target: publishable short paper / thesis chapter on **textbook-to-market verification**.

## 1. Title options
- From Textbook to Live Market: A Reproducible Verification of Wirtschaftsmathematik (Opitz et al., 12th ed.)
- Do Textbook Formulas Survive Contact With 2026 Markets? A Benchmark of Ch.27–30

## 2. Research questions
- RQ1: Are Ch.27 closed forms (Zins/Rente/Tilgung/Kurs/Duration) numerically exact vs live-rate stress?
- RQ2: Does duality hold with zero gap on textbook LPs when solved with modern HiGHS?
- RQ3: How large is the integrality gap + rounding trap on textbook ILPs?
- RQ4: What hidden orderings (duration/coupon/yield, stetig convergence O(1/m)) emerge?
- RQ5: Do BTC/FX live series violate textbook i.i.d./constant-i assumptions, and by how much (MDD/Sharpe)?

## 3. Contributions
- C1: Faithful executable spec of Ch.27 (Sätze 27.3–27.65) + Ch.28–30 algorithms.
- C2: Live snapshot 2026-10-05 (AAPL, BTC-30d, ECB-FX, Sep-2026 hike context) with provenance.
- C3: 4 experiments, 30+ assertions, Docker-pinned reproduction (`docker compose up`).
- C4: 6 hidden patterns H1–H6 with proofs-by-execution.

## 4. Method (zero-to-hero, per 2026 best practice)
1. PLOS 2026 container tips: pin by digest, non-root, dual-tag, Zenodo DOI on release.
2. Tübingen DB reproducibility tutorial: Dockerfile + Compose + Makefile + single automation script.
3. Szyller 2026 repo guide: uv/pip pin, ruff, pytest hot-spots, hydra-style config (here: explicit constants).
4. QuantEval/OptiVerse/FinBench 2026: contamination-free, deterministic backtest config, heterogeneous data.
5. One-search-at-a-time voting: websearch → searxng → openresearch → paper-search → duckduckgo → agent-reach → gitmcp → kaggle → wiki → gsd/superpowers, each with different keywords.

## 5. Threats to validity
- Snapshot is 2026-10-05; live re-fetch may drift (mitigated: snapshot fallback + tolerance bands).
- HiGHS replaces textbook tableau (equivalent by Satz 28.13/28.19; tableau steps documented).
- 2D B&B demo is pedagogical; production MILP needs full solver (documented).

## 6. Future PhD extensions
- Stochastic Zinsen (Vasicek/Hull-White) vs constant-i textbook world.
- Full Gomory loop + cut-pool benchmark on MIPLIB.
- Intraday FX/BTC microstructure vs Dauer-duration immunization.
- LLM textbook-QA (FAMMA-style) on Opitz proofs.
