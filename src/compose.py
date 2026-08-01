"""Algorithm 3: consensus strategy for conflict-aware composition.

For every abstract task the highest-scoring candidate whose conflict degree
stays below theta_Gamma is selected; services opposing an already committed
resource are then pruned. Unassigned tasks fall back to the neutral set psi.
Author: F. Ghedass.
"""
from __future__ import annotations
from dataclasses import dataclass, field

import numpy as np

from . import degrees as dg


@dataclass
class Result:
    picks: dict = field(default_factory=dict)      # task id -> service index
    services: list = field(default_factory=list)
    resources: list = field(default_factory=list)
    trace: list = field(default_factory=list)      # human-readable decisions
    severity: float = 0.0
    score: float = 0.0
    conflict_free: bool = True


def run(sp, co, wc: list, workflow: list, cfg: dict) -> Result:
    """Compose a conflict-free IoT workflow. `co` is the Algorithm 1 output."""
    an = cfg["analysis"]
    w, theta = an["w"], an["theta_gamma"]
    sc = dg.score_service(co.mu_d, co.mu_g, co.mu_p, w)
    caps = {k: set(v) for k, v in sp.caps().items()}
    pool, used, res = set(wc), set(), set()
    out = Result()

    # Most-constrained task first (adjustment A17): committing a resource prunes
    # every service opposing it, so the tasks with the fewest candidates must be
    # served before the pool shrinks. Ties keep the user's original order.
    order = sorted(workflow,
                   key=lambda t: len(pool & caps.get(t["capability"], set())))

    for task in order:
        cand = [s for s in pool if s in caps.get(task["capability"], set())]
        best, best_sc = None, -np.inf
        for s in cand:
            if co.mu_g[s] < theta and sc[s] > best_sc:
                best, best_sc = s, sc[s]
        if best is None:                                   # fallback on psi
            neutral = [s for s in cand if co.region[s] == "psi"]
            if neutral:
                best = min(neutral, key=lambda s: co.mu_g[s])
                out.trace.append(f"{task['task']}: psi fallback -> {sp.sname(best)}")
        if best is None:
            out.trace.append(f"{task['task']}: unassigned (no candidate)")
            continue

        out.picks[task["task"]] = best
        used.add(best)
        new_res = set(np.nonzero(sp.Ir[best])[0].tolist())
        res |= new_res
        out.trace.append(f"{task['task']}: {sp.sname(best)} (score {sc[best]:.3f})")

        # eliminate every candidate conflicting with the committed resources
        drop = {s for s in pool if s != best and co.adj[best, s]}
        if drop:
            out.trace.append("   pruned: " + ", ".join(sorted(sp.sname(s) for s in drop)))
        pool -= drop | {best}

    # Algorithm 3, lines 27-29: unassigned tasks trigger a fallback on the
    # neutral set psi, taking the alternative with the least conflict against
    # the resources already committed. The search stays inside W_c, exactly as
    # the psi fallback of line 15 does: a service rejected by the resource- and
    # QoS-aware filter must not re-enter through the back door.
    wc_set = set(wc)
    for task in workflow:
        if task["task"] in out.picks:
            continue
        able = [s for s in caps.get(task["capability"], set())
                if s in wc_set and s not in used and co.region[s] in ("psi", "delta")]
        safe = [s for s in able if not any(co.adj[s, u] for u in used)]
        if safe:
            pick = min(safe, key=lambda s: (co.mu_g[s], -sc[s]))
            out.picks[task["task"]] = pick
            used.add(pick)
            res |= set(np.nonzero(sp.Ir[pick])[0].tolist())
            out.trace.append(f"{task['task']}: psi/delta fallback -> {sp.sname(pick)}")

    out.services = sorted(used)
    out.resources = sorted(res)
    out.severity = dg.severity(co.mu_d, co.mu_g, out.services)
    out.score = dg.composition_score(sp, co.mu_d, co.mu_g, out.services)
    out.conflict_free = not any(co.adj[a, b] for a in out.services for b in out.services)
    return out
