"""E5 - Impact of the conflict data distribution (Section 8.6).

Five tripartite profiles of the (+1, 0, -1) ratings. Produces Table 20.
Author: F. Ghedass.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from Data.gen_inst import set_density, slice_space      # noqa: E402
from experiments.runner import sweep                    # noqa: E402
from src.conf import load, setup_log                    # noqa: E402
from src.model import Icps                              # noqa: E402
from src.paths import MAIN                              # noqa: E402

TAG = "exp5_distrib"
PROFILES = {"High-Alliance": (0.70, 0.20, 0.10), "Balanced": (0.40, 0.40, 0.20),
            "High-Neutral": (0.20, 0.60, 0.20), "High-Conflict": (0.10, 0.20, 0.70),
            "Realistic": (0.50, 0.30, 0.20)}
POINTS = list(PROFILES)


def run(cfg=None):
    cfg = cfg or load("exp5_distrib.yaml")
    log = setup_log(TAG)
    base = Icps.from_json(MAIN / "icps_main.json")

    def build(pt, rng):
        sp = slice_space(base, cfg["dataset"]["n_services"],
                         cfg["dataset"]["n_resources"], rng)
        return set_density(sp, PROFILES[pt][2], rng, dist=PROFILES[pt]), None

    return sweep(TAG, POINTS, build, cfg, log)


if __name__ == "__main__":
    run()
