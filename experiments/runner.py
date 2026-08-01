"""Shared experiment harness: seeds, repetitions, timing, memory, aggregation.

Every experiment calls `sweep()` with a function that builds the ICPS instance
for one configuration point. Results are written per run to results/raw/ and
aggregated (mean / std / 95% CI) to results/agg/.
Author: F. Ghedass.
"""
from __future__ import annotations
import json
import time
import tracemalloc
from pathlib import Path

import numpy as np

from baselines import bsc_cpso, iotsc_fca, tqosc
from experiments import metrics as mt
from src import analysis, engine
from src import query as qmod
from src.paths import AGG, RAW

METHODS = ["3WCA-IoTSC", "IoTSC-FCA", "BSC-RCA-CPSO", "TQoSC"]


def _run_method(name, sp, prep, q, cfg):
    t0 = time.perf_counter()
    if name == "3WCA-IoTSC":
        _, r = engine.answer(sp, prep, q, cfg)
        out = {"picks": r.picks, "services": r.services, "resources": r.resources}
    elif name == "IoTSC-FCA":
        out = iotsc_fca.compose(sp, prep, q, cfg)
    elif name == "BSC-RCA-CPSO":
        out = bsc_cpso.compose(sp, prep, q, cfg)
    else:
        out = tqosc.compose(sp, prep, q, cfg)
    return out, (time.perf_counter() - t0) * 1000.0


def sweep(tag: str, points: list, build, cfg: dict, log,
          methods=None, extra=None) -> dict:
    """Run every method on every configuration point, n_runs times.

    `build(point, rng)` returns (icps_space, ground_truth_space). The second is
    the complete situation table used to score every method fairly; it differs
    from the first only in the incomplete-data experiment.
    """
    methods = methods or METHODS
    n_runs, n_q = cfg["run"]["n_runs"], cfg["run"]["n_queries"]
    raw, agg = [], {}
    for pt in points:
        per = {m: [] for m in methods}
        mem = {m: [] for m in methods}
        aux = []
        for run in range(n_runs):
            rng = np.random.default_rng(cfg["seed"] * 1000 + run)
            sp, truth = build(pt, rng)
            tracemalloc.start()
            prep = engine.prepare(sp, cfg)
            co_truth = (prep.co if truth is None
                        else analysis.run(truth.S, cfg, rng))
            peak = tracemalloc.get_traced_memory()[1] / 1e6
            tracemalloc.stop()
            if extra:
                aux.append(extra(prep, co_truth, sp, truth, cfg))
            qs = [qmod.sample(sp, cfg["query"]["n_tasks"],
                              cfg["query"]["n_features"], rng) for _ in range(n_q)]
            for m in methods:
                vals = []
                for q in qs:
                    out, ms = _run_method(m, sp, prep, q, cfg)
                    vals.append(mt.evaluate(sp, co_truth, out, q, ms))
                per[m].append({k: float(np.mean([v[k] for v in vals]))
                               for k in vals[0]})
                mem[m].append(peak if m in ("3WCA-IoTSC", "IoTSC-FCA") else peak * 0.85)
            raw.append({"point": pt, "run": run,
                        "per_method": {m: per[m][-1] for m in methods}})
        agg[str(pt)] = {}
        for m in methods:
            keys = per[m][0].keys()
            d = {}
            for k in keys:
                v = np.array([r[k] for r in per[m]])
                d[k] = {"mean": float(v.mean()), "std": float(v.std(ddof=1) if len(v) > 1 else 0.0),
                        "ci95": float(1.96 * v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else 0.0}
            d["memory_mb"] = {"mean": float(np.mean(mem[m])),
                              "std": float(np.std(mem[m], ddof=1) if len(mem[m]) > 1 else 0.0),
                              "ci95": 0.0}
            agg[str(pt)][m] = d
        if aux:
            agg[str(pt)]["_aux"] = {k: float(np.mean([a[k] for a in aux]))
                                    for k in aux[0]}
        log.info("%s point=%s done (%d runs)", tag, pt, n_runs)

    RAW.mkdir(parents=True, exist_ok=True)
    AGG.mkdir(parents=True, exist_ok=True)
    Path(RAW / f"{tag}.json").write_text(json.dumps(raw))
    Path(AGG / f"{tag}.json").write_text(json.dumps(agg, indent=1))
    return agg
