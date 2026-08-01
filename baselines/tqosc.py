"""Baseline 1 - TQoSC: combinatorial-auction QoS-based IoT service composition.

Reimplementation of the mechanism of
https://github.com/tiber10/A-combinatorial-auction-based-approach-for-IoT-Service-composition
Services bid on the abstract tasks with a utility derived from their quality
attributes (response time, cost, reliability); winner determination is a greedy
allocation maximising total utility under one-service-per-task.

This method is conflict-agnostic by construction: it never reads the situation
table K^c. Test/test_baselines.py asserts that this module does not import the
conflict machinery.
Author: F. Ghedass.
"""
from __future__ import annotations
import numpy as np

NAME = "TQoSC"


def utility(sp, i: int) -> float:
    """Bid value of a service: the classical QoS aggregate, nothing else."""
    q = sp.services[i]["qos"]
    return 0.25 * ((1 - q["cost"]) + q["availability"] + (1 - q["time"]) + q["reliability"])


def compose(sp, prep, query: dict, cfg: dict) -> dict:
    caps = sp.caps()
    bids = []
    for t in query["workflow"]:
        for s in caps.get(t["capability"], []):
            bids.append((utility(sp, s), t["task"], s))
    bids.sort(reverse=True)                      # winner determination, greedy

    picks, taken = {}, set()
    for _, task, s in bids:
        if task not in picks and s not in taken:
            picks[task] = s
            taken.add(s)
    res = set()
    for s in picks.values():
        res |= set(np.nonzero(sp.Ir[s])[0].tolist())
    return {"picks": picks, "services": sorted(set(picks.values())),
            "resources": sorted(res), "trace": [f"auction: {len(bids)} bids"]}
