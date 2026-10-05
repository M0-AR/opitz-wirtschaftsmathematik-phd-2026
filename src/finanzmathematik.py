"""Finanzmathematik — faithful implementation of Opitz et al. Ch.27.

Covers: Einfachzins/Zinseszins (27.1), Abschreibung (27.2),
Aequivalenzprinzip Bar/End/Zeitwert + mittlerer Zinstermin + Duration (27.3),
Kapitalwert + interner Zins (27.4), Renten (27.5), Tilgung (27.6), Kurs/Rendite (27.7).

All formulas are textbook-first; variable names follow the book (K, q, i, r, R, S, C0...).
No hand-waving: every function is unit-tested in tests/test_finanzmathematik.py.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


# ---------------------------------------------------------------- 27.1 Zins
def einfachzins_endwert(K0: float, i: float, n: float) -> float:
    """Kn = K0*(1+n*i) — Definition 27.2."""
    return K0 * (1.0 + n * i)


def zinseszins_endwert(K0: float, i: float, n: float) -> float:
    """Kn = K0*q^n, q=1+i — Definition 27.4."""
    return K0 * ((1.0 + i) ** n)


def zinseszins_barwert(Kn: float, i: float, n: float) -> float:
    return Kn * ((1.0 + i) ** (-n))


def laufzeit_aus_endwert(K0: float, Kn: float, i: float) -> float:
    """n = (ln Kn - ln K0)/ln q — Satz 27.5."""
    q = 1.0 + i
    return (math.log(Kn) - math.log(K0)) / math.log(q)


def sparbuch_gemischt(K0: float, i: float, t1_days: float, n_full: int, t2_days: float) -> float:
    """K = K0*(1+i*t1/360)*(1+i)^n*(1+i*t2/360) — Definition 27.8."""
    return K0 * (1 + i * t1_days / 360.0) * ((1 + i) ** n_full) * (1 + i * t2_days / 360.0)


def relativ_periodenzins(i_nom: float, m: int) -> float:
    return i_nom / m


def effektiv_jahreszins(i_nom: float, m: int) -> float:
    """i_eff = (1+i/m)^m - 1 — Definition 27.10."""
    return (1.0 + i_nom / m) ** m - 1.0


def konform_periodenzins(i_nom: float, m: int) -> float:
    """i_kon = (1+i)^{1/m} - 1."""
    return (1.0 + i_nom) ** (1.0 / m) - 1.0


def stetig_endwert(K0: float, i: float, n: float) -> float:
    """lim_{m->inf} K0*(1+i/m)^{m*n} = K0*exp(i*n) — Definition 27.13."""
    return K0 * math.exp(i * n)


def effektiv_aus_stetig(i_nom: float) -> float:
    return math.exp(i_nom) - 1.0


def konform_aus_effektiv(i_eff: float) -> float:
    return math.log(1.0 + i_eff)


# ------------------------------------------------------------ 27.2 Abschreibung
def linear_abschreibung(K0: float, Kn: float, n: int) -> dict:
    """Satz 27.17: a = (K0-Kn)/n constant."""
    a = (K0 - Kn) / n
    ks = [K0 - t * a for t in range(n + 1)]
    return {"rate": a, "i0": a / K0, "werte": ks}


def degressiv_abschreibung(K0: float, i: float, n: int) -> dict:
    """Satz 27.19: Kt = K0*(1-i)^t."""
    ks = [K0 * ((1 - i) ** t) for t in range(n + 1)]
    aas = [ks[t - 1] - ks[t] for t in range(1, n + 1)]
    return {"werte": ks, "raten": aas, "i_rest": i}


def degressiv_satz_aus_restwert(K0: float, Kn: float, n: int) -> float:
    return 1.0 - (Kn / K0) ** (1.0 / n)


# --------------------------------------- 27.3 Aequivalenzprinzip / Duration
def barwert(zahlungen: list[float], i: float) -> float:
    """K0 = sum At*q^-t — Definition 27.22."""
    q = 1 + i
    return sum(a * (q ** (-t)) for t, a in enumerate(zahlungen))


def endwert(zahlungen: list[float], i: float) -> float:
    n = len(zahlungen) - 1
    return barwert(zahlungen, i) * ((1 + i) ** n)


def zeitwert(zahlungen: list[float], i: float, s: int) -> float:
    return barwert(zahlungen, i) * ((1 + i) ** s)


def mittlerer_zinstermin(zahlungen: list[float], i: float) -> float:
    """Satz 27.26: q^m = sum At / sum At q^-t."""
    q = 1 + i
    s = sum(zahlungen)
    k0 = barwert(zahlungen, i)
    if s <= 0 or k0 <= 0:
        raise ValueError("mittlerer Zinstermin needs positive sums")
    return (math.log(s) - math.log(k0)) / math.log(q)


def duration(zahlungen: list[float], i: float) -> float:
    """Satz 27.29: d = sum t*At q^-t / K0."""
    q = 1 + i
    k0 = barwert(zahlungen, i)
    if k0 == 0:
        raise ValueError("duration undefined for K0=0")
    return sum(t * a * (q ** (-t)) for t, a in enumerate(zahlungen)) / k0


# ------------------------------------------------- 27.4 Kapitalwert/interner Zins
def kapitalwert(perioden: list[float], i: float) -> float:
    """G = sum Pt q^-t — Definition 27.33."""
    return barwert(perioden, i)


def interner_zins(perioden: list[float], lo: float = -0.9, hi: float = 5.0, tol: float = 1e-10) -> float:
    """Bisection on G(i)=0. Textbook uses Regula falsi (3.20); bisection is equivalent + robust.

    Requires sign change in (lo,hi]. Raises if none (cf. Satz 27.37 conditions).
    """
    glo = kapitalwert(perioden, lo)
    ghi = kapitalwert(perioden, hi)
    if glo == 0:
        return lo
    if ghi == 0:
        return hi
    if glo * ghi > 0:
        # try to expand hi
        for _ in range(60):
            hi = hi * 2 + 0.5
            ghi = kapitalwert(perioden, hi)
            if glo * ghi <= 0:
                break
        else:
            raise ValueError(f"no sign change: G({lo})={glo}, G({hi})={ghi}; check Satz 27.37")
    for _ in range(500):
        mid = 0.5 * (lo + hi)
        gm = kapitalwert(perioden, mid)
        if abs(gm) < 1e-12 or (hi - lo) < tol:
            return mid
        if glo * gm <= 0:
            hi, ghi = mid, gm
        else:
            lo, glo = mid, gm
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------- 27.5 Renten
def renten_endwert_nach(r: float, i: float, n: int) -> float:
    """Rn = r*(q^n-1)/(q-1) — Definition 27.39 nachschuessig."""
    q = 1 + i
    if i == 0:
        return r * n
    return r * (q**n - 1) / (q - 1)


def renten_endwert_vor(r: float, i: float, n: int) -> float:
    return renten_endwert_nach(r, i, n) * (1 + i)


def renten_barwert_nach(r: float, i: float, n: int) -> float:
    return renten_endwert_nach(r, i, n) * ((1 + i) ** (-n))


def renten_barwert_vor(r: float, i: float, n: int) -> float:
    return renten_endwert_vor(r, i, n) * ((1 + i) ** (-n))


def ersatzrate_nach(r: float, i: float, m: int) -> float:
    """re = r*(m + i/2*(m-1)) — Definition 27.42."""
    return r * (m + i / 2 * (m - 1))


def ersatzrate_vor(r: float, i: float, m: int) -> float:
    return r * (m + i / 2 * (m + 1))


def renten_endwert_arithmetisch(r: float, d: float, i: float, n: int) -> float:
    """Satz 27.46 nachschuessig."""
    q = 1 + i
    if i == 0:
        return n * r + d * n * (n - 1) / 2
    return r * (q**n - 1) / (q - 1) + d / (q - 1) * ((q**n - 1) / (q - 1) - n)


def renten_endwert_geometrisch(r: float, g: float, i: float, n: int) -> float:
    """Satz 27.49 nachschuessig."""
    q = 1 + i
    if abs(g - q) < 1e-14:
        return r * (q ** (n - 1)) * n
    return r * (g**n - q**n) / (g - q)


def ewige_rente_barwert_nach(r: float, i: float) -> float:
    """Satz 27.51: R0 = r/i."""
    return r / i


def ewige_rente_barwert_vor(r: float, i: float) -> float:
    return r * (1 + i) / i


# ---------------------------------------------------------------- 27.6 Tilgung
@dataclass
class TilgungsZeile:
    k: int
    rest_beginn: float
    zins: float
    tilgung: float
    annuitaet: float


def ratentilgung_plan(S: float, i: float, n: int) -> list[TilgungsZeile]:
    """Definition 27.56: T = S/n constant."""
    T = S / n
    plan, rest = [], S
    for k in range(1, n + 1):
        z = rest * i
        plan.append(TilgungsZeile(k, rest, z, T, T + z))
        rest -= T
    return plan


def annuitaet(S: float, i: float, n: int) -> float:
    """Satz 27.59a: A = S*q^n*(q-1)/(q^n-1)."""
    q = 1 + i
    return S * (q**n) * (q - 1) / (q**n - 1)


def annuitaetentilgung_plan(S: float, i: float, n: int) -> list[TilgungsZeile]:
    A = annuitaet(S, i, n)
    q = 1 + i
    plan, rest = [], S
    for k in range(1, n + 1):
        z = rest * i
        t = A - z
        # last-period rounding guard
        if k == n:
            t = rest
            A_last = t + z
            plan.append(TilgungsZeile(k, rest, z, t, A_last))
            rest = 0.0
        else:
            plan.append(TilgungsZeile(k, rest, z, t, A))
            rest = rest * q - A
    return plan


def restschuld_annuitaet(S: float, i: float, n: int, k: int) -> float:
    """Satz 27.59b: Rk = S*(q^n - q^{k-1})/(q^n - 1), k=1-indexed Beginn."""
    q = 1 + i
    return S * (q**n - q ** (k - 1)) / (q**n - 1)


# ---------------------------------------------------------------- 27.7 Kurs
def emissionskurs(c: float, Cn: float, i: float, n: int) -> float:
    """Satz 27.62a: C0 = c*q^-n*(q^n-1)/(q-1) + Cn*q^-n."""
    q = 1 + i
    return c * (q**-n) * (q**n - 1) / (q - 1) + Cn * (q**-n)


def bond_duration(c: float, Cn: float, i: float, n: int) -> float:
    """Satz 27.65."""
    q = 1 + i
    c0 = emissionskurs(c, Cn, i, n)
    num = sum(t * c * (q ** (-t)) for t in range(1, n)) + n * (c + Cn) * (q ** (-n))
    return num / c0


def bankenformel(c: float, C: float, Cn: float, n: int) -> float:
    """Definition 27.67a: qa = 1 + c/C + (Cn-C)/(100*n)."""
    return 1 + c / C + (Cn - C) / (100 * n)


def boersenformel(c: float, C: float, Cn: float, n: int) -> float:
    """Definition 27.67b: qb = 1 + c/C + (Cn-C)/(C*n)."""
    return 1 + c / C + (Cn - C) / (C * n)
