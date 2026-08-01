"""Paired significance tests between 3WCA-IoTSC and each baseline.

Wilcoxon signed-rank on the per-run means, with the matched-pairs rank-biserial
correlation as the effect size. Exact p-values are reported; a non-significant
difference is never described as an improvement.
Author: F. Ghedass.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import AGG, RAW        # noqa: E402

BASE = ["IoTSC-FCA", "BSC-RCA-CPSO", "TQoSC"]
KEYS = ["success", "severity", "score", "n_conflicts", "time_ms"]


def main():
    out = {}
    for f in sorted(RAW.glob("exp*.json")):
        raw = json.loads(f.read_text())
        if not raw or "3WCA-IoTSC" not in raw[0]["per_method"]:
            continue
        res = {}
        for key in KEYS:
            ours = np.array([r["per_method"]["3WCA-IoTSC"][key] for r in raw])
            for b in BASE:
                if b not in raw[0]["per_method"]:
                    continue
                theirs = np.array([r["per_method"][b][key] for r in raw])
                d = ours - theirs
                if np.allclose(d, 0):
                    res[f"{key} vs {b}"] = {"p": 1.0, "effect": 0.0,
                                            "note": "identical samples"}
                    continue
                stat, p = wilcoxon(ours, theirs, zero_method="zsplit")
                n = int((d != 0).sum())
                eff = float(np.sign(d).sum() / max(n, 1))
                res[f"{key} vs {b}"] = {
                    "p": float(p), "effect_rank_biserial": eff,
                    "mean_diff": float(d.mean()), "n_pairs": len(d),
                    "significant_at_0.05": bool(p < 0.05)}
        out[f.stem] = res
    (AGG / "stats_tests.json").write_text(json.dumps(out, indent=1))
    for exp, r in out.items():
        sig = sum(1 for v in r.values() if v.get("significant_at_0.05"))
        print(f"  {exp}: {sig}/{len(r)} comparisons significant at p<0.05")


if __name__ == "__main__":
    main()
