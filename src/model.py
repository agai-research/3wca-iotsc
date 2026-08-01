"""ICPS space: services, IoT resources, features and the Pawlak situation table.

Entities of Section 5 of the paper:
  K^r = (S, R, I_r)  Def. 5.1 | K^f = (S, F, I_f)  Def. 5.2
  K^c = (S, R, c)    Def. 5.3 with c: S x R -> {-1, 0, +1}
Author: F. Ghedass.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass
class Icps:
    services: list        # {id, name, capability, domain, qos{}, features[], resources[]}
    resources: list       # {id, name, type, protocol, format, compliance[], energy}
    features: list        # {id, name}
    S: np.ndarray         # situation table |S| x |R| in {-1, 0, +1}
    Ir: np.ndarray        # incidence S x R (bool)
    If: np.ndarray        # incidence S x F (bool)
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        self.si = {s["id"]: i for i, s in enumerate(self.services)}
        self.ri = {r["id"]: i for i, r in enumerate(self.resources)}
        self.fi = {f["id"]: i for i, f in enumerate(self.features)}

    @property
    def ns(self) -> int:
        return len(self.services)

    @property
    def nr(self) -> int:
        return len(self.resources)

    def sname(self, i: int) -> str:
        return self.services[i]["id"]

    def rname(self, j: int) -> str:
        return self.resources[j]["id"]

    def caps(self) -> dict:
        """capability -> service indices able to fulfil it."""
        out: dict = {}
        for i, s in enumerate(self.services):
            out.setdefault(s["capability"], []).append(i)
        return out

    def to_json(self, path: Path) -> None:
        ent = [[self.sname(i), self.rname(j), int(self.S[i, j])]
               for i, j in zip(*np.nonzero(self.S))]
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps({
            "meta": self.meta, "services": self.services,
            "resources": self.resources, "features": self.features,
            "situation": {"encoding": "sparse-triples",
                          "shape": [int(x) for x in self.S.shape], "entries": ent}}))

    @classmethod
    def from_json(cls, path: Path) -> "Icps":
        d = json.loads(Path(path).read_text())
        svc, res, fea = d["services"], d["resources"], d["features"]
        si = {s["id"]: i for i, s in enumerate(svc)}
        ri = {r["id"]: j for j, r in enumerate(res)}
        fi = {f["id"]: k for k, f in enumerate(fea)}
        S = np.zeros((len(svc), len(res)), dtype=np.int8)
        for a, b, v in d["situation"]["entries"]:
            S[si[a], ri[b]] = v
        Ir = np.zeros_like(S, dtype=bool)
        If = np.zeros((len(svc), len(fea)), dtype=bool)
        for s in svc:
            for r in s["resources"]:
                Ir[si[s["id"]], ri[r]] = True
            for f in s["features"]:
                If[si[s["id"]], fi[f]] = True
        return cls(svc, res, fea, S, Ir, If, d.get("meta", {}))
