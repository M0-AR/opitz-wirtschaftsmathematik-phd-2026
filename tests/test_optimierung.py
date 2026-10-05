import numpy as np
from src.optimierung import (
    primal_dual_production, transport_optimal, kkt_example_2927,
    branch_and_bound_2d,
)


def test_lp_duality():
    r = primal_dual_production()
    assert r["primal"].success and r["dual"].success
    assert abs(r["x_star"][0] - 3) < 1e-6
    assert abs(r["x_star"][1] - 4) < 1e-6
    assert r["gap"] < 1e-6


def test_transport():
    C = np.array([[7, 2, 4, 7], [9, 5, 3, 3], [7, 7, 6, 4]], float)
    tp = transport_optimal(C, [10, 8, 7], [6, 5, 8, 6])
    assert abs(tp["cost_nw"] - 106) < 1e-9
    assert abs(tp["cost_opt"] - 100) < 1e-6


def test_kkt():
    r = kkt_example_2927()
    assert r.success
    assert abs(r.x[0] - 4) < 1e-4 and abs(r.x[1] - 2) < 1e-4


def test_bb():
    bb = branch_and_bound_2d([2, 3], [[1, 2], [2, 1]], [8, 9])
    assert abs(bb["f_best"] - 13) < 1e-6
