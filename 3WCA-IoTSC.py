#!/usr/bin/env python3
"""Entry point: run the 3WCA-IoTSC prototype on one user query.

  python 3WCA-IoTSC.py --query Test/queries/q1.json --space Data/main/classroom.json
Author: F. Ghedass.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src import query as qmod, report              # noqa: E402
from src.conf import load, setup_log               # noqa: E402
from src.engine import answer, prepare             # noqa: E402
from src.model import Icps                         # noqa: E402
from src.paths import MAIN, RESULTS, ensure        # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description="conflict-aware IoT service composition")
    ap.add_argument("--space", default=str(MAIN / "classroom.json"),
                    help="ICPS space JSON (default: the smart-classroom fixture)")
    ap.add_argument("--query", default="Test/queries/q1.json")
    ap.add_argument("--config", default="default.yaml")
    ap.add_argument("--out", default=str(RESULTS / "composition.txt"))
    ap.add_argument("--log-level", default="INFO")
    args = ap.parse_args()

    ensure()
    log = setup_log("prototype", args.log_level)
    cfg = load(args.config)
    sp = Icps.from_json(Path(args.space))
    log.info("ICPS space loaded: |S|=%d |R|=%d |F|=%d", sp.ns, sp.nr, len(sp.features))

    prep = prepare(sp, cfg)
    log.info("lattices built in %.3f s (|L^r|=%d |L^f|=%d |L^c|=%d)",
             prep.timing["lattice_s"], prep.timing["n_cpt_r"],
             prep.timing["n_cpt_f"], prep.timing["n_cpt_c"])
    log.info("3WCA analysis: |Delta|=%d |Gamma|=%d |psi|=%d",
             len(prep.co.delta), len(prep.co.gamma), len(prep.co.psi))

    q = qmod.load(Path(args.query))
    wc, res = answer(sp, prep, q, cfg)
    txt = report.render(sp, prep.co, wc, res, cfg)
    print(txt)
    Path(args.out).write_text(txt)
    Path(args.out).with_suffix(".json").write_text(json.dumps({
        "query": q["query_id"],
        "C_IoT": [sp.sname(i) for i in res.services],
        "resources": [sp.rname(j) for j in res.resources],
        "severity": res.severity, "score": res.score,
        "conflict_free": res.conflict_free,
        "picks": {k: sp.sname(v) for k, v in res.picks.items()}}, indent=1))
    log.info("composition written to %s", args.out)


if __name__ == "__main__":
    main()
