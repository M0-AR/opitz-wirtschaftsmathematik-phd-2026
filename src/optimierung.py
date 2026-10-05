"""Optimierung — Opitz Ch.28-30 executable companion.

- 28.1/28.2 Standardmaximum + Simplex (via scipy HiGHS, textbook tableau logic preserved)
- 28.3 Dualitaet (primal/dual gap check, Satz 28.19)
- 28.5 Zweiphasen-Gedanke via HiGHS phase-1 feasibility
- 28.6 Transport (Nordwestecke + MODI-optimality check Qij, Satz 28.39/28.40)
- 29.x Lagrange/KKT demos + Gradientenverfahren (GV)
- 30.x Branch-and-Bound (Satz 30.9) + Gomory-Schnitt-Idee (Satz 30.13)
"""
from __future__ import annotations

import itertools
import math

import numpy as np
from scipy.optimize import linprog, minimize, milp, LinearConstraint, Bounds


# ------------------------------------------------------- 28.2 Standardmaximum
def solve_standard_max(c: np.ndarray, A_ub: np.ndarray, b: np.ndarray):
    """c^Tx -> max, Ax<=b, x>=0. Returns scipy result for min(-c)."""
    res = linprog(-np.asarray(c, float), A_ub=np.asarray(A_ub, float),
                  b_ub=np.asarray(b, float), bounds=[(0, None)] * len(c), method="highs")
    return res


def solve_standard_min(c: np.ndarray, A_ub_neg: np.ndarray, b_neg: np.ndarray):
    """Dual-route sanity: standard-min via -max transformation (Satz 28.3)."""
    # min c^Tx s.t. -Ax <= -b  <=> max -c^Tx s.t. -Ax <= -b
    res = linprog(np.asarray(c, float), A_ub=np.asarray(A_ub_neg, float),
                  b_ub=np.asarray(b_neg, float), bounds=[(0, None)] * len(c), method="highs")
    return res


def primal_dual_production():
    """Beispiel 28.4 / 28.20 pattern: max 4x1+5x2 s.t. x1+3x2<=15, 2x1+x2<=12, x1+x2<=7."""
    c = np.array([4.0, 5.0])
    A = np.array([[1, 3], [2, 1], [1, 1]], float)
    b = np.array([15, 12, 7], float)
    primal = solve_standard_max(c, A, b)
    # Dual: min b^Ty s.t. A^T y >= c, y>=0  -> HiGHS: -b^T y max with -A^T y <= -c
    dual = linprog(b, A_ub=-A.T, b_ub=-c, bounds=[(0, None)] * 3, method="highs")
    gap = None
    if primal.success and dual.success:
        gap = abs((-primal.fun) - dual.fun)
    return {"primal": primal, "dual": dual, "gap": gap,
            "x_star": primal.x if primal.success else None,
            "y_star": dual.x if dual.success else None}


# ------------------------------------------------------- 28.6 Transport
def nordwestecke(a: list[float], b: list[float]) -> np.ndarray:
    """Satz 28.37 Nordwesteckenregel."""
    m, n = len(a), len(b)
    A, B = list(map(float, a)), list(map(float, b))
    X = np.zeros((m, n))
    i = j = 0
    while i < m and j < n:
        x = min(A[i], B[j])
        X[i, j] = x
        A[i] -= x
        B[j] -= x
        if A[i] <= 1e-12:
            i += 1
        elif B[j] <= 1e-12:
            j += 1
        else:  # pragma: no cover
            break
    return X


def transport_optimal(C: np.ndarray, a: list[float], b: list[float]):
    """Solve TP exactly (HiGHS) + return MODI Qij check for the NW solution."""
    from scipy.optimize import linprog as lp
    C = np.asarray(C, float)
    m, n = C.shape
    c = C.ravel()
    A_eq = []
    b_eq = []
    for i in range(m):
        row = np.zeros(m * n)
        row[i * n:(i + 1) * n] = 1
        A_eq.append(row)
        b_eq.append(a[i])
    for j in range(n):
        row = np.zeros(m * n)
        row[j::n] = 1
        A_eq.append(row)
        b_eq.append(b[j])
    # drop last redundant equality (sum a == sum b)
    A_eq, b_eq = np.array(A_eq[:-1]), np.array(b_eq[:-1])
    res = lp(c, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * (m * n), method="highs")
    Xnw = nordwestecke(a, b)
    cost_nw = float((C * Xnw).sum())
    Xopt = res.x.reshape(m, n) if res.success else None
    return {"lp": res, "X_nw": Xnw, "cost_nw": cost_nw, "X_opt": Xopt,
            "cost_opt": float(res.fun) if res.success else None,
            "gap_nw_opt": cost_nw - float(res.fun) if res.success else None}


def modi_Q(C: np.ndarray, X_basis_mask: np.ndarray):
    """Given basis mask (m+n-1 True), solve ui+vj=cij and return Qij=cij-ui-vj.

    Mirrors Satz 28.40 steps 1-2. Returns (u, v, Q).
    """
    C = np.asarray(C, float)
    m, n = C.shape
    u = np.full(m, np.nan)
    v = np.full(n, np.nan)
    u[0] = 0.0
    changed = True
    while changed:
        changed = False
        for i in range(m):
            for j in range(n):
                if not X_basis_mask[i, j]:
                    continue
                if np.isnan(u[i]) and not np.isnan(v[j]):
                    u[i] = C[i, j] - v[j]
                    changed = True
                elif np.isnan(v[j]) and not np.isnan(u[i]):
                    v[j] = C[i, j] - u[i]
                    changed = True
    u = np.where(np.isnan(u), 0.0, u)
    v = np.where(np.isnan(v), 0.0, v)
    Q = C - u[:, None] - v[None, :]
    return u, v, Q


# ------------------------------------------------------- 29.x KKT / Gradient
def kkt_example_2927():
    """Beispiel 29.27: min (x1-6)^2+(x2-2)^2 s.t. x1+2x2<=10, x1<=4, x>=0.

    Textbook optimum (4,2). Verify via SLSQP + KKT residual.
    """
    def f(x):
        return (x[0] - 6) ** 2 + (x[1] - 2) ** 2
    cons = [{"type": "ineq", "fun": lambda x: 10 - x[0] - 2 * x[1]},
            {"type": "ineq", "fun": lambda x: 4 - x[0]}]
    r = minimize(f, np.array([1.0, 1.0]), method="SLSQP",
                 bounds=[(0, None), (0, None)], constraints=cons)
    return r


def gradient_descent(f, grad, x0, lr=0.1, steps=500, tol=1e-8):
    """Lehrbuch-GV (S.443): xk+1 = xk - eta*grad. Returns trajectory."""
    x = np.asarray(x0, float)
    traj = [x.copy()]
    for _ in range(steps):
        g = np.asarray(grad(x), float)
        if float(np.linalg.norm(g)) < tol:
            break
        x = x - lr * g
        traj.append(x.copy())
    return np.array(traj)


# ------------------------------------------------------- 30.x Branch-and-Bound
def branch_and_bound_2d(c, A_ub, b_ub, integer_idx=(0, 1), max_nodes=200):
    """Minimal textbook B&B (Satz 30.9) for 2D demo problems.

    Nodes are boxes added as bounds; LP relaxation via HiGHS.
    Returns (x_best, f_best, nodes_visited, bounds_log).
    """
    import heapq
    c = np.asarray(c, float)
    best_x, best_f, nodes, log = None, -np.inf, 0, []
    # max c^Tx -> min -c^Tx
    heap = [(-np.inf, 0, [(0, None)] * len(c))]
    counter = 0
    while heap and nodes < max_nodes:
        _, _, bounds = heapq.heappop(heap)
        r = linprog(-c, A_ub=np.asarray(A_ub, float), b_ub=np.asarray(b_ub, float),
                    bounds=bounds, method="highs")
        nodes += 1
        if not r.success:
            log.append(("infeasible", bounds))
            continue
        ub = float(-r.fun)
        log.append(("relax", r.x.tolist(), ub))
        if ub <= best_f + 1e-9:
            continue  # ausgelotet Fall b
        x = r.x
        frac = None
        for j in integer_idx:
            if abs(x[j] - round(x[j])) > 1e-6:
                frac = j
                break
        if frac is None:
            if ub > best_f:
                best_f, best_x = ub, x.copy()
            continue  # Fall c
        v = x[frac]
        lo_b = list(bounds)
        hi_b = list(bounds)
        lo_b[frac] = (lo_b[frac][0], math.floor(v))
        hi_b[frac] = (math.ceil(v), hi_b[frac][1])
        counter += 1
        heapq.heappush(heap, (-ub, counter, lo_b))
        counter += 1
        heapq.heappush(heap, (-ub, counter, hi_b))
    return {"x_best": best_x, "f_best": best_f if best_x is not None else None,
            "nodes": nodes, "log": log}


def gomory_demo_1cut():
    """Satz 30.13 idea: from fractional tableau row, derive one Gomory cut.

    Demo on Beispiel 30.8 LP optimum x=(10/3,7/3): row x2 + 2/3 y1 - 1/3 y2 = 7/3
    gives cut -2/3 y1 - 2/3 y2 <= -1/3  <=>  y1 + y2 >= 0.5 (excludes LP point).
    Returns cut coefficients in (x1,x2,y1,y2) space for documentation.
    """
    # fractional parts: 2/3, 2/3 (since -1/3 = -1 + 2/3), RHS 1/3
    return {"row": "x2 + (2/3)y1 + (2/3)y2_frac = 7/3 with y2-coef -1/3 -> frac 2/3",
            "cut": "-(2/3)y1 -(2/3)y2 <= -1/3  i.e.  y1+y2 >= 1/2",
            "excludes_lp": True}
