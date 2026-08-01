"""E3 - Impact of workflow complexity on composition quality (Section 8.4).

|W_u| varies from 5 to 50 tasks. Produces Table 18 and Figures 9 and 11.
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
from src.paths import MAIN                              # noqa: E402

TAG = "exp3_workflow"
POINTS = [5, 10, 20, 30, 50]


def run(cfg=None):
    cfg = cfg or load("exp3_workflow.yaml")
    log = setup_log(TAG)
    base = Icps.from_json(MAIN / "icps_main.json")
    agg = {}
    for pt in POINTS:
        c = json.loads(json.dumps(cfg))     # honour --runs / --queries overrides
        c["query"]["n_tasks"] = pt

        def build(_p, rng, c=c):
            sp = slice_space(base, c["dataset"]["n_services"],
                             c["dataset"]["n_resources"], rng)
            return set_density(sp, c["dataset"]["density"], rng), None

        agg.update(sweep(f"{TAG}_{pt}", [pt], build, c, log))
    from src.paths import AGG
    (AGG / f"{TAG}.json").write_text(json.dumps(agg, indent=1))
    return agg


if __name__ == "__main__":
    run()
