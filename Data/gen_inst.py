"""Derive per-experiment instances from the main ICPS dataset.

Every experiment needs its own slice: a given number of entities, a given
conflict density, a given tripartite distribution, or a partially erased
situation table. Instances are plain sub-samples of the main dataset so that
all methods see exactly the same ICPS space.
Author: F. Ghedass.
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.model import Icps            # noqa: E402


def slice_space(sp: Icps, ns: int, nr: int, rng) -> Icps:
    """Take the first ns services and nr resources, keeping every relation."""
    ns, nr = min(ns, sp.ns), min(nr, sp.nr)
    si = np.arange(ns)
    rj = np.arange(nr)
    S = sp.S[np.ix_(si, rj)].copy()
    Ir = sp.Ir[np.ix_(si, rj)].copy()
    If = sp.If[si].copy()
    res = [sp.resources[j] for j in rj]
    keep = {r["id"] for r in res}
    svc = []
    for i in si:
        s = dict(sp.services[i])
        s["resources"] = [r for r in s["resources"] if r in keep]
        svc.append(s)
    return Icps(svc, res, list(sp.features), S, Ir, If, dict(sp.meta))


def set_density(sp: Icps, sigma: float, rng, dist=None) -> Icps:
    """Resample the stances so that `sigma` of the defined entries are -1.

    Only the cells of I_r carry a stance (a provider declares an opinion on the
    devices its service actually consumes), so the density is expressed over
    those cells - see adjustment A15.
    """
    out = Icps(list(sp.services), list(sp.resources), list(sp.features),
               sp.S.copy(), sp.Ir.copy(), sp.If.copy(), dict(sp.meta))
    cells = np.argwhere(out.Ir)
    if dist is None:
        rest = 1.0 - sigma
        p = [0.5 / 0.8 * rest, 0.3 / 0.8 * rest, sigma]
    else:
        p = list(dist)
    vals = rng.choice([1, 0, -1], size=len(cells), p=np.array(p) / np.sum(p))
    out.S[:] = 0
    for (i, j), v in zip(cells, vals):
        out.S[i, j] = v
    return out


def drop_entries(sp: Icps, pct: float, rng) -> Icps:
    """Erase `pct` of the declared stances; missing knowledge becomes 0."""
    out = Icps(list(sp.services), list(sp.resources), list(sp.features),
               sp.S.copy(), sp.Ir.copy(), sp.If.copy(), dict(sp.meta))
    cells = np.argwhere(out.S != 0)
    if len(cells):
        k = int(round(pct * len(cells)))
        for i, j in cells[rng.choice(len(cells), size=k, replace=False)]:
            out.S[i, j] = 0
    return out
