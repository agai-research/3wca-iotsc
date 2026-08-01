"""Baseline 3 - BSC-RCA-CPSO: Relational Concept Analysis + Composite PSO.

Reimplementation of Gharbi & Mezni, "Towards Big Services Composition"
(the approach cited as FFCA-IoTSC in the paper and renamed here). Two formal
contexts form the relational context family: K^B (services x QoS levels,
Def. 6.1) and K^D (services x domains, Def. 6.2); the lattices L^B and L^D are
derived, candidate services are extracted from L^D (Algorithm 1), composite and
independent particles are built (Algorithm 2), evaluated with the Simple
Additive Weight fitness, and improved by the worst-fit self-adjustment loop.

Adapted to the ICPS setting: big services -> ICPS services, domains -> IoT
capability categories, data sources -> IoT resources. Like TQoSC it is
conflict-agnostic and never reads K^c.
Author: F. Ghedass.
"""
from __future__ import annotations
import numpy as np

from src import lattice as lt

NAME = "BSC-RCA-CPSO"
_LAT_CACHE: dict = {}          # RCA lattices are rebuilt only when the space changes
QOS_KEYS = ("cost", "availability", "time", "reliability")


def _contexts(sp):
    """K^B (service x scaled QoS) and K^D (service x domain) of the RCF."""
    q = np.array([[sp.services[i]["qos"][k] for k in QOS_KEYS] for i in range(sp.ns)])
    med = np.median(q, axis=0)
    kb = np.zeros((sp.ns, 2 * len(QOS_KEYS)), dtype=bool)
    kb[:, 0::2] = q >= med          # "high" level of the criterion
    kb[:, 1::2] = q < med           # "low" level
    doms = sorted({s["domain"] for s in sp.services})
    kd = np.zeros((sp.ns, len(doms)), dtype=bool)
    for i, s in enumerate(sp.services):
        kd[i, doms.index(s["domain"])] = True
    return kb, kd


_QOS_CACHE: dict = {}


def _qos_matrix(sp) -> np.ndarray:
    """QoS vectors as a matrix, built once per ICPS space."""
    key = id(sp)
    if key not in _QOS_CACHE:
        _QOS_CACHE.clear()
        _QOS_CACHE[key] = np.array(
            [[s["qos"][k] for k in QOS_KEYS] for s in sp.services], dtype=float)
    return _QOS_CACHE[key]


def _fitness(sp, comp, w=(0.25, 0.25, 0.25, 0.25)) -> float:
    """Eq. (2) of the source paper: sequential QoS aggregation, SAW model."""
    if len(comp) == 0:
        return 0.0
    c = _qos_matrix(sp)[list(comp)]
    n = len(comp)
    cost, avail, time, rel = c[:, 0], c[:, 1], c[:, 2], c[:, 3]
    return float(w[0] * (1 - cost.sum() / n) + w[1] * avail.prod() ** (1 / n)
                 + w[2] * (1 - time.sum() / n) + w[3] * rel.prod() ** (1 / n))


def compose(sp, prep, query: dict, cfg: dict) -> dict:
    rng = np.random.default_rng(cfg.get("seed", 0))
    lc = cfg["lattice"]
    key = id(sp)
    if key not in _LAT_CACHE:
        kb, kd = _contexts(sp)
        _LAT_CACHE.clear()                       # one space at a time
        _LAT_CACHE[key] = (lt.build(kb, lc["min_support"], min(lc["cap"], 400)),
                           lt.build(kd, lc["min_support"], min(lc["cap"], 400)))
    lat_b, lat_d = _LAT_CACHE[key]
    caps = sp.caps()

    # -- Algorithm 1: candidate extraction, top-down parse of L^D -------------
    cand: dict = {}
    for t in query["workflow"]:
        able = set(caps.get(t["capability"], []))
        pool: set = set()
        for ext, _ in lat_d:                       # extents, largest first
            pool |= (set(ext) & able)
            if len(pool) >= 8:
                break
        cand[t["task"]] = sorted(pool) or sorted(able)

    # -- Algorithm 2: composite particles + independent particles -------------
    n_part = int(cfg.get("cpso", {}).get("n_particles", 8))
    max_it = int(cfg.get("cpso", {}).get("max_iter", 12))
    swarm = []
    for _ in range(n_part):
        cp = {t: int(rng.choice(v)) for t, v in cand.items() if v}
        swarm.append(cp)
    indep = {t: [s for s in v] for t, v in cand.items()}

    best, best_fit = None, -np.inf
    for _ in range(max_it):
        improved = False
        for cp in swarm:
            f0 = _fitness(sp, list(cp.values()))
            # worst elementary particle, replaced by the fittest unused one
            if cp:
                q = _qos_matrix(sp)
                solo = lambda i: 0.25 * ((1 - q[i, 0]) + q[i, 1] + (1 - q[i, 2]) + q[i, 3])
                worst = min(cp, key=lambda t: solo(cp[t]))
                for alt in sorted(indep.get(worst, []), key=lambda s: -solo(s))[:4]:
                    if alt == cp[worst]:
                        continue
                    trial = dict(cp)
                    trial[worst] = alt
                    if _fitness(sp, list(trial.values())) > f0:
                        cp.update(trial)
                        improved = True
                        break
            f = _fitness(sp, list(cp.values()))
            if f > best_fit:
                best, best_fit = dict(cp), f
        if not improved:
            break

    picks = best or {}
    res = set()
    for s in picks.values():
        res |= set(np.nonzero(sp.Ir[s])[0].tolist())
    return {"picks": picks, "services": sorted(set(picks.values())),
            "resources": sorted(res),
            "trace": [f"CPSO fitness={best_fit:.3f}, |L^B|={len(lat_b)}, |L^D|={len(lat_d)}"]}
