"""Configuration loading. Nothing in src/ may hardcode a parameter. Author: F. Ghedass."""
from __future__ import annotations
import copy
import logging
import yaml

from .paths import CONFIG, LOGS


def _merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in over.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load(name: str = "default.yaml", **over) -> dict:
    """default.yaml, then the named config, then keyword overrides."""
    cfg = yaml.safe_load((CONFIG / "default.yaml").read_text())
    if name and name != "default.yaml":
        cfg = _merge(cfg, yaml.safe_load((CONFIG / name).read_text()) or {})
    return _merge(cfg, over) if over else cfg


def setup_log(tag: str = "run", level: str = "INFO") -> logging.Logger:
    """One log file per run, plus console output."""
    LOGS.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger(tag)
    if log.handlers:
        return log
    log.setLevel(level)
    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(name)s | %(message)s", "%H:%M:%S")
    fh, sh = logging.FileHandler(LOGS / f"{tag}.log", mode="w"), logging.StreamHandler()
    for h in (fh, sh):
        h.setFormatter(fmt)
        log.addHandler(h)
    return log
