"""Conflict, coalition and neutrality degrees, severity and score (Eqs. 1-8).

Readings adopted for the type-ambiguous equations (see docs/adjustments.md):
  mu_Gamma(s) = share of the generators of Gamma in which s participates  (A1)
  mu_Delta(s) = share of Delta members allied with s on some resource      (A2)
  mu_psi(s)   = share of psi members neutral with s on some resource       (A3)
Author: F. Ghedass.
"""
from __future__ import annotations
import numpy as np


def c_global(S: np.ndarray, i: int, rs) -> float:
    """Eq. 1: global view of service i over a set of IoT resources."""
    rs = list(rs)
    return float(S[i, rs].mean()) if rs else 0.0


def mu_gamma(gamma: list, ns: int) -> np.ndarray:
    """Eq. 3, reading A1."""
    out = np.zeros(ns)
    if not gamma:
        return out
    for a, b, _ in gamma:
        out[a] += 1
        out[b] += 1
    return out / len(gamma)


def mu_delta(ally: np.ndarray, delta) -> np.ndarray:
    """Eq. 4, reading A2."""
    ns = ally.shape[0]
    d = list(delta)
    out = np.zeros(ns)
    if not d:
        return out
    sub = ally[:, d].copy()
    for i in d:                       # a service is not its own ally
        sub[i, d.index(i)] = False
    return sub.sum(axis=1) / len(d)


def mu_psi(S: np.ndarray, psi) -> np.ndarray:
    """Eq. 5, reading A3: phi_r(s,x) = 0 for at least one resource."""
    ns = S.shape[0]
    p = list(psi)
    out = np.zeros(ns)
    if not p:
        return out
    nz = (S != 0)
    for x in p:
        # phi = 0 <=> the product of the two stances is 0 on some resource
        neutral = ~(nz & nz[x])
        hit = neutral.any(axis=1)
        hit[x] = False
        out += hit
    return out / len(p)


def score_service(md: np.ndarray, mg: np.ndarray, mp: np.ndarray, w) -> np.ndarray:
    """Algorithm 3 line 9: w1.mu_Delta - w2.mu_Gamma - w3.mu_psi."""
    return w[0] * md - w[1] * mg - w[2] * mp


def severity(md: np.ndarray, mg: np.ndarray, comp) -> float:
    """Eq. 7: Sev(C_IoT)."""
    c = list(comp)
    return float(sum(md[i] * mg[i] for i in c) / len(c)) if c else 0.0


def qos_score(sp, comp) -> float:
    """Normalised SAW quality of a composition, in [0, 1] (reading A5)."""
    c = list(comp)
    if not c:
        return 0.0
    vals = []
    for i in c:
        q = sp.services[i]["qos"]
        vals.append(0.25 * ((1 - q["cost"]) + q["availability"]
                            + (1 - q["time"]) + q["reliability"]))
    return float(np.mean(vals))


def composition_score(sp, md, mg, comp) -> float:
    """Eq. 8, normalised: severity term combined with the aggregated QoS."""
    c = list(comp)
    if not c:
        return 0.0
    return float((1.0 - severity(md, mg, c)) * qos_score(sp, c))
