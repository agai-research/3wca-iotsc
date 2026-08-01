"""Baseline 2 - IoTSC-FCA: our approach without conflict consideration.

Ablation study. The situation table is omitted and the conflict knowledge
(coalitions, conflict sets, neutral sets) is neglected: the ICPS space is
represented as two ordinary formal contexts K^r and K^f from which the lattices
L^r and L^f are derived, exactly as in 3WCA-IoTSC, and the candidate services
returned by Algorithm 2 are then ranked on QoS alone.

Isolating precisely the contribution of the conflict machinery is the point, so
the shared stages are reused verbatim from src/.
Author: F. Ghedass.
"""
from __future__ import annotations
import numpy as np
from sklearn.preprocessing import MinMaxScaler

from src import filter as flt

NAME = "IoTSC-FCA"


def _qos_rank(sp, cand: list) -> dict:
    """Normalised QoS score for the candidate services (scikit-learn scaling)."""
    if not cand:
        return {}
    m = np.array([[sp.services[i]["qos"][k] for k in
                   ("cost", "availability", "time", "reliability", "throughput")]
                  for i in cand], dtype=float)
    z = MinMaxScaler().fit_transform(m)
    z[:, 0] = 1 - z[:, 0]        # cost and time are cost-type criteria
    z[:, 2] = 1 - z[:, 2]
    return {s: float(v) for s, v in zip(cand, z.mean(axis=1))}


def compose(sp, prep, query: dict, cfg: dict) -> dict:
    # same lattice-based filtering as the full approach (Algorithm 2)
    wc = flt.run(sp, prep.lat_r, prep.lat_f, query["workflow"], set(query["features"]))
    caps = sp.caps()
    rank = _qos_rank(sp, wc)
    picks, pool = {}, set(wc)
    for t in query["workflow"]:
        cand = [s for s in pool if s in set(caps.get(t["capability"], []))]
        if not cand:                       # fall back outside W_c, still no conflict check
            cand = [s for s in caps.get(t["capability"], []) if s not in picks.values()]
            rank.update(_qos_rank(sp, cand))
        if cand:
            best = max(cand, key=lambda s: rank.get(s, 0.0))
            picks[t["task"]] = best
            pool.discard(best)
    res = set()
    for s in picks.values():
        res |= set(np.nonzero(sp.Ir[s])[0].tolist())
    return {"picks": picks, "services": sorted(set(picks.values())),
            "resources": sorted(res), "trace": [f"|W_c|={len(wc)} (no conflict analysis)"]}
