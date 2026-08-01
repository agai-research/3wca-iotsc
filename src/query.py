"""User query handling: an abstract IoT workflow W_u plus requested features F_u.
Author: F. Ghedass."""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np

REQUIRED = ("query_id", "workflow", "features")


def load(path: Path) -> dict:
    q = json.loads(Path(path).read_text())
    return validate(q)


def validate(q: dict) -> dict:
    missing = [k for k in REQUIRED if k not in q]
    if missing:
        raise ValueError(f"query is missing the field(s): {', '.join(missing)}")
    if not q["workflow"]:
        raise ValueError("query workflow is empty")
    for t in q["workflow"]:
        if "task" not in t or "capability" not in t:
            raise ValueError(f"malformed task in workflow: {t}")
    return q


def sample(sp, n_tasks: int, n_feats: int, rng) -> dict:
    """Draw a realistic, satisfiable user request from the ICPS space.

    The requested features are taken from the widely supported ones (a user asks
    for open protocols and compliance, not for exotic combinations), and the
    abstract tasks are drawn from the capabilities actually offered by the
    services that possess those features. The request is therefore answerable,
    which is what makes the comparison between the four methods meaningful.
    """
    freq = sp.If.sum(axis=0)
    top = np.argsort(-freq)[:max(n_feats * 3, n_feats)]
    fsel = rng.choice(top, size=min(n_feats, len(top)), replace=False)
    eligible = np.nonzero(sp.If[:, fsel].all(axis=1))[0]
    if len(eligible) == 0:
        eligible = np.arange(sp.ns)

    caps = sp.caps()
    avail = sorted({sp.services[i]["capability"] for i in eligible})
    picked = rng.choice(avail, size=min(n_tasks, len(avail)), replace=False)
    wf = []
    for k, c in enumerate(picked):
        pool = [i for i in caps[c] if i in set(eligible.tolist())] or caps[c]
        owner = sp.services[int(rng.choice(pool))]
        rs = owner["resources"]
        wf.append({"task": f"a{k + 1}", "capability": str(c),
                   "resource": str(rng.choice(rs)) if len(rs) else None})
    return {"query_id": "rnd", "workflow": wf,
            "features": [sp.features[int(j)]["id"] for j in fsel]}
