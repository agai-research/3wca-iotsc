"""E6 - Impact of the completeness of the situation table (Section 8.7).

10% to 40% of the declared stances are erased. For 3WCA-IoTSC the missing
knowledge is read as neutral (0), following Pawlak's conservative approach.
Every method is still scored against the *complete* table, which is what makes
the degradation and the false ally / false conflict rates meaningful.
Produces Table 21.
Author: F. Ghedass.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from Data.gen_inst import drop_entries, set_density, slice_space   # noqa: E402
from experiments.metrics import false_rates                        # noqa: E402
from experiments.runner import sweep                               # noqa: E402
from src.conf import load, setup_log                               # noqa: E402
from src.model import Icps                                         # noqa: E402
from src.paths import MAIN                                         # noqa: E402

TAG = "exp6_missing"
POINTS = [0, 10, 20, 30, 40]


def _false(prep, co_truth, sp, truth, cfg):
    fa, fc = false_rates(prep.co, co_truth, sp.ns)
    return {"false_allies": fa, "false_conflicts": fc}


def run(cfg=None):
    cfg = cfg or load("exp6_missing.yaml")
    log = setup_log(TAG)
    base = Icps.from_json(MAIN / "icps_main.json")

    def build(pt, rng):
        sp = slice_space(base, cfg["dataset"]["n_services"],
                         cfg["dataset"]["n_resources"], rng)
        full = set_density(sp, cfg["dataset"]["density"], rng)
        return drop_entries(full, pt / 100.0, rng), full

    return sweep(TAG, POINTS, build, cfg, log, extra=_false)


if __name__ == "__main__":
    run()
