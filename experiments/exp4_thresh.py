"""E4 - Effect of the thresholds t1 and t2 on coalition formation (Section 8.5).

t1 and t2 are parameters of Algorithm 1 and therefore exist only in
3WCA-IoTSC; the baselines have no coalition thresholds, so - exactly as in
Table 19 of the paper - this experiment covers our approach alone.
Produces Table 19 and Figures 12 and 13.
Author: F. Ghedass.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from Data.gen_inst import set_density, slice_space      # noqa: E402
from experiments.runner import sweep                    # noqa: E402
from src.conf import load, setup_log                    # noqa: E402
from src.model import Icps                              # noqa: E402
from src.paths import AGG, MAIN                         # noqa: E402

TAG = "exp4_thresh"
POINTS = [(0.1, 0.9), (0.2, 0.8), (0.3, 0.7), (0.4, 0.6)]


def _sets(prep, co, sp, truth, cfg):
    return {"delta": len(co.delta), "gamma": len(co.gamma), "psi": len(co.psi)}


def run(cfg=None):
    log = setup_log(TAG)
    base = Icps.from_json(MAIN / "icps_main.json")
    agg = {}
    cfg = cfg or load("exp4_thresh.yaml")
    for t1, t2 in POINTS:
        c = json.loads(json.dumps(cfg))     # honour --runs / --queries overrides
        c["analysis"]["t1"], c["analysis"]["t2"] = t1, t2

        def build(_p, rng, c=c):
            sp = slice_space(base, c["dataset"]["n_services"],
                             c["dataset"]["n_resources"], rng)
            return set_density(sp, c["dataset"]["density"], rng), None

        agg.update(sweep(f"{TAG}_{t1}_{t2}", [(t1, t2)], build, c, log,
                         methods=["3WCA-IoTSC"], extra=_sets))
    (AGG / f"{TAG}.json").write_text(json.dumps(agg, indent=1))
    return agg


if __name__ == "__main__":
    run()
