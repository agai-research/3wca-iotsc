"""Run every experiment of Section 8 and write the aggregated results.
Author: F. Ghedass."""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.conf import load, setup_log      # noqa: E402
from src.paths import ensure              # noqa: E402

EXPS = ["exp1_density", "exp2_scale", "exp3_workflow",
        "exp4_thresh", "exp5_distrib", "exp6_missing"]


def main() -> None:
    ap = argparse.ArgumentParser(description="run the 3WCA-IoTSC experiments")
    ap.add_argument("--only", nargs="*", default=EXPS, choices=EXPS)
    ap.add_argument("--runs", type=int, help="override run.n_runs")
    ap.add_argument("--queries", type=int, help="override run.n_queries")
    args = ap.parse_args()
    ensure()
    log = setup_log("main-exp")
    import importlib
    for name in args.only:
        mod = importlib.import_module(f"experiments.{name}")
        cfg = load(f"{name}.yaml")
        if args.runs:
            cfg["run"]["n_runs"] = args.runs
        if args.queries:
            cfg["run"]["n_queries"] = args.queries
        t0 = time.perf_counter()
        mod.run(cfg)
        log.info("%s finished in %.1f s", name, time.perf_counter() - t0)


if __name__ == "__main__":
    main()
