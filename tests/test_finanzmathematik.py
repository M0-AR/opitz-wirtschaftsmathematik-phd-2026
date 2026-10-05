import math
from src.finanzmathematik import (
    einfachzins_endwert, zinseszins_endwert, effektiv_jahreszins,
    konform_periodenzins, stetig_endwert, barwert, duration,
    mittlerer_zinstermin, kapitalwert, interner_zins,
    renten_endwert_nach, annuitaet, restschuld_annuitaet,
    emissionskurs, bond_duration, linear_abschreibung,
    degressiv_satz_aus_restwert,
)


def test_zins_anchors():
    assert einfachzins_endwert(20000, 0.06, 10) == 32000
    assert abs(zinseszins_endwert(20000, 0.06, 10) - 35816.95) < 0.05
    assert abs(effektiv_jahreszins(0.06, 4) - 0.0614) < 0.0005
    assert abs(konform_periodenzins(0.06, 4) - 0.0147) < 0.0005
    assert abs(stetig_endwert(20000, 0.06, 5) - 26997.18) < 0.6


def test_aequivalenz():
    At = [0, 1000, 0, 1000, 0, 1000]
    k0 = barwert(At, 0.05)
    assert abs(k0 - 2599.74) < 0.5
    d = duration(At, 0.05)
    m = mittlerer_zinstermin(At, 0.05)
    assert 2.5 < d < 3.5 and 2.5 < m < 3.5


def test_kapital_intern():
    P = [-20000, 6000, 8000, 9000]
    assert abs(kapitalwert(P, 0.05) - 745.06) < 1.0
    assert kapitalwert(P, 0.08) < 0
    iz = interner_zins(P)
    assert abs(iz - 0.0685) < 0.002


def test_rente_tilgung_kurs():
    assert abs(renten_endwert_nach(1000, 0.05, 5) - 5525.63) < 0.02
    assert abs(annuitaet(40000, 0.05, 5) - 9238.99) < 0.05
    assert abs(restschuld_annuitaet(40000, 0.05, 5, 1) - 40000) < 1e-9
    assert abs(emissionskurs(5, 100, 0.04, 4) - 103.63) < 0.03
    assert bond_duration(5, 100, 0.06, 4) < bond_duration(5, 100, 0.04, 4)


def test_abschreibung():
    assert abs(linear_abschreibung(12000, 2000, 5)["rate"] - 2000) < 1e-9
    assert abs(degressiv_satz_aus_restwert(12000, 2000, 5) - 0.30117) < 0.002
