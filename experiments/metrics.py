"""The metric dictionary - one definition, applied identically to all methods.

Every metric is evaluated against the *ground-truth* situation table, including
for the methods that ignore conflicts. That is exactly how a conflict-blind
composition gets penalised.
Author: F. Ghedass.
"""
from __future__ import annotations
import numpy as np

from src import degrees as dg


def evaluate(sp, co, out: dict, query: dict, elapsed_ms: float) -> dict:
    """Metrics of Tables 16 to 21 for a single composition."""
    svc = list(out["services"])
    n_tasks = len(query["workflow"])
    bound = len(out["picks"])

    pairs = [(a, b) for k, a in enumerate(svc) for b in svc[k + 1:] if co.adj[a, b]]
    conflict_free = not pairs
    success = (bound == n_tasks) and conflict_free

    regions = [co.region[s] for s in svc] or ["psi"]
    allied = 100.0 * sum(r == "delta" for r in regions) / len(regions)
    neutral = 100.0 * sum(r == "psi" for r in regions) / len(regions)

    # a selection is "conflicting" when it introduces an opposing pair
    conflicting = len({s for p in pairs for s in p})
    avoidance = 100.0 * (1 - conflicting / max(len(svc), 1))

    need = set()
    for t in query["workflow"]:
        if t.get("resource") and t["resource"] in sp.ri:
            need.add(sp.ri[t["resource"]])
    used = set(out["resources"])
    eff = 100.0 * len(need & used) / max(len(used), 1)

    return {
        "success": float(success),
        # Success conflates two distinct failures. Reporting them apart is what
        # shows the actual trade-off: 3WCA-IoTSC never returns a conflicting
        # composition, but occasionally cannot bind a task whose only candidates
        # were pruned, whereas the conflict-blind methods always bind and
        # sometimes ship a conflict.
        "conflict_free": float(conflict_free),
        "bound_ratio": bound / max(n_tasks, 1),
        "severity": dg.severity(co.mu_d, co.mu_g, svc),
        "time_ms": elapsed_ms,
        "n_conflicts": float(len(pairs)),
        "resources_used": float(len(used)),
        "services_used": float(len(svc)),
        "score": dg.composition_score(sp, co.mu_d, co.mu_g, svc),
        "allied_usage": allied,
        "neutral_usage": neutral,
        "conflict_avoidance": avoidance,
        "resource_efficiency": eff,
    }


def false_rates(co_partial, co_full, ns: int) -> tuple:
    """False allies / false conflicts under an incomplete situation table."""
    part, full = co_partial.adj, co_full.adj
    iu = np.triu_indices(ns, 1)
    p, f = part[iu], full[iu]
    n_pairs = max(len(p), 1)
    false_ally = 100.0 * float(((~p) & f).sum()) / n_pairs
    false_conf = 100.0 * float((p & (~f)).sum()) / n_pairs
    return false_ally, false_conf
