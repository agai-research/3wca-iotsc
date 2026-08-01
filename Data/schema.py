"""Minimal structural validation of the generated dataset. Author: F. Ghedass."""
from __future__ import annotations

SERVICE_KEYS = {"id", "name", "capability", "domain", "qos", "features", "resources"}
RESOURCE_KEYS = {"id", "name", "type", "protocol", "format", "compliance", "energy"}
QOS_KEYS = {"cost", "availability", "time", "reliability", "throughput"}


def check(d: dict) -> list:
    """Return the list of problems found; empty list means the dataset is valid."""
    bad = []
    for key in ("meta", "services", "resources", "features", "situation"):
        if key not in d:
            bad.append(f"missing top-level key: {key}")
    if bad:
        return bad
    rids = {r["id"] for r in d["resources"]}
    fids = {f["id"] for f in d["features"]}
    for s in d["services"][:200]:
        if not SERVICE_KEYS <= set(s):
            bad.append(f"service {s.get('id')} misses {SERVICE_KEYS - set(s)}")
        if not QOS_KEYS <= set(s.get("qos", {})):
            bad.append(f"service {s.get('id')} has an incomplete qos vector")
        if set(s["resources"]) - rids:
            bad.append(f"service {s['id']} points at unknown resources")
        if set(s["features"]) - fids:
            bad.append(f"service {s['id']} points at unknown features")
    for r in d["resources"][:200]:
        if not RESOURCE_KEYS <= set(r):
            bad.append(f"resource {r.get('id')} misses {RESOURCE_KEYS - set(r)}")
    vals = {v for _, _, v in d["situation"]["entries"]}
    if not vals <= {-1, 0, 1}:
        bad.append(f"situation table holds values outside -1/0/+1: {vals}")
    return bad
