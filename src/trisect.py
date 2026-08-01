"""Three-way trisection of the ICPS services (Section 5.2 of the paper).

Provides S_r^-, S_r^0, S_r^+ and their pairwise unions, the multi-resource
trisection S_R^*, the auxiliary function phi_r of Def. 4.2 / Table 6, the
conflict generators, and the conflict measure m(E) of Eq. 2.
Author: F. Ghedass.
"""
from __future__ import annotations
from math import comb

import numpy as np


def trisection(S: np.ndarray, j: int) -> tuple:
    """(S_r^-, S_r^0, S_r^+) for the IoT resource of column j."""
    col = S[:, j]
    return (np.nonzero(col == -1)[0], np.nonzero(col == 0)[0], np.nonzero(col == 1)[0])


def weak(neg, neu, pos) -> dict:
    """The three weak coalitions obtained by pairwise union."""
    return {"-0": np.union1d(neg, neu), "-+": np.union1d(neg, pos),
            "0+": np.union1d(neu, pos)}


def tri_multi(S: np.ndarray, rs) -> tuple:
    """S_R^-, S_R^+, S_R^0 for a set R of IoT resources."""
    sub = S[:, list(rs)]
    neg = np.nonzero((sub == -1).all(axis=1))[0]
    pos = np.nonzero((sub == 1).all(axis=1))[0]
    neu = np.setdiff1d(np.arange(S.shape[0]), np.union1d(neg, pos))
    return neg, pos, neu


def phi(S: np.ndarray, i: int, k: int, j: int) -> int:
    """Def. 4.2 / Table 6: 1 agreement, 0 partial or neutral, -1 conflict."""
    if i == k:
        return 1
    p = int(S[i, j]) * int(S[k, j])
    return 1 if p == 1 else (-1 if p == -1 else 0)


def conflict_matrix(S: np.ndarray) -> np.ndarray:
    """A[i,k] = True iff services i and k oppose each other on some resource."""
    pos = (S == 1).astype(np.float32)
    neg = (S == -1).astype(np.float32)
    a = (pos @ neg.T) + (neg @ pos.T)
    a = a > 0
    np.fill_diagonal(a, False)
    return a


def ally_matrix(S: np.ndarray) -> np.ndarray:
    """B[i,k] = True iff i and k both support the same resource (phi_r = 1)."""
    pos = (S == 1).astype(np.float32)
    b = (pos @ pos.T) > 0
    np.fill_diagonal(b, False)
    return b


def generators(S: np.ndarray) -> list:
    """Minimal conflict generators (s_i, s_j, r), i.e. every opposing pair."""
    out = []
    for j in range(S.shape[1]):
        neg, _, pos = trisection(S, j)
        if len(neg) and len(pos):
            for a in neg:
                for b in pos:
                    lo, hi = (int(a), int(b)) if a < b else (int(b), int(a))
                    out.append((lo, hi, int(j)))
    return sorted(set(out))


def mu_resource(S: np.ndarray) -> np.ndarray:
    """Conflict density induced by each resource: |S_r^-|.|S_r^+| / C(|S|,2)."""
    n = S.shape[0]
    denom = comb(n, 2) if n > 1 else 1
    neg = (S == -1).sum(axis=0).astype(float)
    pos = (S == 1).sum(axis=0).astype(float)
    return (neg * pos) / denom


def m_measure(adj: np.ndarray, e) -> float:
    """Eq. 2: density of conflicting ordered pairs inside the service set E."""
    e = list(e)
    if not e:
        return 0.0
    sub = adj[np.ix_(e, e)]
    return float(sub.sum()) / (len(e) ** 2)
