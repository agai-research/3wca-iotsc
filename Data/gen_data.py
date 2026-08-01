"""Generation of the hybrid ICPS dataset used by 3WCA-IoTSC.

Two products:
  * classroom()  - the smart-classroom fixture of Section 6.4 (8 services,
                   10 IoT resources), used by the first-test script;
  * generate()   - the augmented ICPS dataset described in Section 8.1: Yelp-like
                   business services enriched with CASAS/CIC-IoT style devices.

The public corpora cannot be downloaded from this environment, so the records
are synthesised from domain knowledge following the paper's recipe (1-5 devices
per service, protocol / format / compliance / energy annotations, three-valued
stances). Provenance of every field is documented in docs/dataset-card.md.
Author: F. Ghedass.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.conf import load, setup_log          # noqa: E402
from src.model import Icps                    # noqa: E402
from src.paths import MAIN, ensure            # noqa: E402

PROTO = ["Zigbee", "Bluetooth", "Wi-Fi", "Z-Wave", "LoRaWAN"]
FORMAT = ["JSON", "XML", "CBOR"]
COMPLY = ["GDPR", "HIPAA", "PDPL", "CCPA"]
RTYPE = ["sensor", "actuator", "display", "network", "power", "wearable"]

# Capability catalogue of the ICPS space. Smart education (the paper's
# illustration domain) is deliberately the densest dimension. A workflow of up
# to 50 abstract tasks must be expressible, so the catalogue is large enough to
# draw 50 distinct capabilities.
EDU = ["broadcasting", "assessment", "display", "occupancy", "comfort",
       "whiteboarding", "acoustics", "attendance", "lms_gateway", "ebook",
       "voice_typing", "lecture_capture", "exam_proctoring", "roster_sync",
       "captioning", "translation", "lab_booking", "device_checkout",
       "campus_wayfinding", "study_room", "plagiarism_check", "grade_analytics",
       "podium_control", "classroom_air", "projection_calib"]
LIV = ["lighting", "security_cam", "entertainment", "door_lock", "thermostat",
       "smart_plug", "voice_assistant", "leak_detect", "robot_vacuum", "garden"]
HLT = ["vitals", "medication", "fall_detect", "telehealth", "ehr_sync",
       "glucose", "sleep_track", "rehab_coach", "ward_alert", "pharmacy"]
MOB = ["mobility", "parking", "eticket", "fleet_track", "traffic_light",
       "bike_share", "ev_charge", "route_plan"]
ECO = ["metering", "billing", "market_feed", "supply_track", "retail_beacon",
       "energy_trade"]
GOV = ["permits", "civic_alert", "waste_route", "air_quality", "flood_watch",
       "streetlight"]
IND = ["asset_health", "line_control", "soil_moisture", "irrigation",
       "crop_metrics", "cold_chain"]
CAPS = ([(c, "smart_education") for c in EDU] + [(c, "smart_living") for c in LIV]
        + [(c, "smart_healthcare") for c in HLT] + [(c, "smart_mobility") for c in MOB]
        + [(c, "smart_economy") for c in ECO] + [(c, "smart_governance") for c in GOV]
        + [(c, "smart_industry") for c in IND])

FEATNAMES = ["open protocol", "regulatory compliance", "low latency",
             "energy aware", "LMS interoperability", "data mediation",
             "edge processing", "encryption", "multi-tenant", "audit trail"]


def classroom() -> Icps:
    """The smart classroom of Section 6.4 (Tables 10, 11 and 12)."""
    svc = ["LS", "CB", "QG", "RM", "SL", "NG", "CC", "PC"]
    full = ["LiveStream", "CollabBoard", "QuizGame", "RoomMonitor",
            "SmartLight", "NoiseGuard", "ClimateCtrl", "ProjCtrl"]
    cap = ["broadcasting", "whiteboarding", "assessment", "occupancy",
           "comfort", "acoustics", "comfort", "display"]
    res = ["MS", "AH", "WC", "PG", "TS", "MG", "AL", "DS", "MB", "EP"]
    rfull = ["MainScreen", "AudioHub", "WiFiCore", "PowerGrid", "ThermSensor",
             "MotionGrid", "AmbientLight", "DrawSurface", "MicBeam", "EnergyPack"]
    # Table 11 - situation table, columns in the order above
    tab = [
        [1, 1, 1, 1, 0, 0, 0, 0, 1, 0],    # LS
        [1, 0, 1, -1, 0, 0, 0, 1, 0, 0],   # CB
        [1, 1, 1, 0, 0, 0, 0, 0, 0, 1],    # QG
        [0, 0, 1, 1, 1, 1, 1, 0, 0, 0],    # RM
        [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],    # SL
        [0, -1, 0, 1, 0, 0, 0, 0, 1, 0],   # NG
        [0, 0, 0, 1, 1, -1, 0, 0, 0, 0],   # CC
        [1, 0, 0, 1, 0, 0, 1, 0, 0, 0],    # PC
    ]
    # Table 12 - feature formal context
    feats = {"LS": ["f1", "f2", "f3", "f5"], "CB": ["f1", "f2", "f3"],
             "QG": ["f1", "f2", "f5"], "RM": ["f1", "f2", "f4"],
             "SL": ["f1", "f2", "f4"], "NG": ["f2", "f3", "f4"],
             "CC": ["f1", "f2", "f4"], "PC": ["f1", "f2", "f3"]}
    S = np.array(tab, dtype=np.int8)
    fea = [{"id": f"f{k+1}", "name": n} for k, n in enumerate(
        ["open protocol", "regulatory compliance", "low latency",
         "energy aware", "LMS interoperability"])]
    resources = [{"id": r, "name": rf, "type": RTYPE[k % len(RTYPE)],
                  "protocol": PROTO[k % len(PROTO)], "format": FORMAT[k % len(FORMAT)],
                  "compliance": ["GDPR"], "energy": round(0.2 + 0.05 * k, 2)}
                 for k, (r, rf) in enumerate(zip(res, rfull))]
    services = []
    for i, s in enumerate(svc):
        own = [res[j] for j in range(len(res)) if S[i, j] == 1]   # claimed resources
        services.append({"id": s, "name": full[i], "capability": cap[i],
                         "domain": "smart_education",
                         "qos": {"cost": 0.3, "availability": 0.95, "time": 0.2,
                                 "reliability": 0.9, "throughput": 0.8},
                         "features": feats[s], "resources": own})
    Ir = (S == 1)
    If = np.zeros((8, 5), dtype=bool)
    for i, s in enumerate(svc):
        for f in feats[s]:
            If[i, int(f[1:]) - 1] = True
    return Icps(services, resources, fea, S, Ir, If,
                {"name": "smart-classroom fixture", "source": "paper Section 6.4"})


def generate(cfg: dict) -> Icps:
    """Augmented ICPS dataset (Section 8.1)."""
    d = cfg["dataset"]
    rng = np.random.default_rng(cfg["seed"])
    ns, nr, nf = d["n_services"], d["n_resources"], d["n_features"]
    lo, hi = d["res_per_service"]
    flo, fhi = d["feat_per_service"]
    pplus, pzero, pminus = d["dist"]

    features = [{"id": f"f{k+1}", "name": FEATNAMES[k % len(FEATNAMES)]}
                for k in range(nf)]
    resources = [{"id": f"r{j+1}", "name": f"device_{j+1}",
                  "type": str(rng.choice(RTYPE)), "protocol": str(rng.choice(PROTO)),
                  "format": str(rng.choice(FORMAT)),
                  "compliance": [str(x) for x in rng.choice(COMPLY, size=rng.integers(1, 3),
                                                            replace=False)],
                  "energy": round(float(rng.uniform(0.05, 0.95)), 3)}
                 for j in range(nr)]

    # IoT resources are not consumed uniformly: a smart environment has "hot"
    # devices (power rail, audio hub, wireless backbone) claimed by many
    # services, exactly as PowerGrid is in the running example. Popularity is
    # therefore Zipf-skewed - see adjustment A15.
    alpha = float(d.get("popularity_alpha", 0.9))
    pop = 1.0 / np.power(np.arange(1, nr + 1), alpha)
    pop = pop / pop.sum()

    S = np.zeros((ns, nr), dtype=np.int8)
    Ir = np.zeros((ns, nr), dtype=bool)
    If = np.zeros((ns, nf), dtype=bool)
    services = []
    # the stance distribution is renormalised so that exactly `density` of the
    # *defined* stances are -1 (see adjustment A15)
    sigma = d["density"]
    rest = 1.0 - sigma
    p = [pplus / (pplus + pzero) * rest, pzero / (pplus + pzero) * rest, sigma]
    for i in range(ns):
        k = int(rng.integers(lo, hi + 1))
        cols = rng.choice(nr, size=k, replace=False, p=pop)
        stance = rng.choice([1, 0, -1], size=k, p=p)
        S[i, cols] = stance
        Ir[i, cols] = True
        fk = int(rng.integers(flo, fhi + 1))
        fcols = rng.choice(nf, size=min(fk, nf), replace=False)
        If[i, fcols] = True
        cap, dom = CAPS[int(rng.integers(0, len(CAPS)))]
        services.append({
            "id": f"s{i+1}", "name": f"{cap}_svc_{i+1}", "capability": cap,
            "domain": dom,
            "qos": {"cost": round(float(rng.uniform(0.05, 0.95)), 3),
                    "availability": round(float(rng.uniform(0.80, 0.999)), 3),
                    "time": round(float(rng.uniform(0.05, 0.95)), 3),
                    "reliability": round(float(rng.uniform(0.75, 0.999)), 3),
                    "throughput": round(float(rng.uniform(0.2, 1.0)), 3)},
            "features": [f"f{j+1}" for j in np.nonzero(If[i])[0]],
            "resources": [f"r{j+1}" for j in cols],
        })
    meta = {"seed": cfg["seed"], "generator": "gen_data.py v1.0",
            "provenance": {"services": "synthesised, Yelp-business style",
                           "devices": "synthesised, CASAS / CIC-IoT-2022 style",
                           "stances": "sampled, three-valued Pawlak ratings"},
            "params": d}
    return Icps(services, resources, features, S, Ir, If, meta)


def stats(sp: Icps) -> dict:
    """Entity counts for the manuscript."""
    tot = int(sp.Ir.sum())
    return {
        "n_services": sp.ns, "n_resources": sp.nr, "n_features": len(sp.features),
        "defined_stances": tot,
        "plus": int(((sp.S == 1) & sp.Ir).sum()),
        "zero": int(((sp.S == 0) & sp.Ir).sum()),
        "minus": int(((sp.S == -1) & sp.Ir).sum()),
        "pct_minus": round(100.0 * ((sp.S == -1) & sp.Ir).sum() / max(tot, 1), 2),
        "mean_res_per_service": round(float(sp.Ir.sum(axis=1).mean()), 3),
        "mean_feat_per_service": round(float(sp.If.sum(axis=1).mean()), 3),
        "n_capabilities": len(sp.caps()),
        "fill_Ir": round(float(sp.Ir.mean()), 5),
        "fill_If": round(float(sp.If.mean()), 5),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="generate the ICPS dataset")
    ap.add_argument("--config", default="default.yaml")
    ap.add_argument("--seed", type=int)
    args = ap.parse_args()
    cfg = load(args.config)
    if args.seed is not None:
        cfg["seed"] = args.seed
    ensure()
    log = setup_log("gen_data")

    fx = classroom()
    fx.to_json(MAIN / "classroom.json")
    log.info("classroom fixture written (|S|=%d, |R|=%d)", fx.ns, fx.nr)

    sp = generate(cfg)
    sp.to_json(MAIN / "icps_main.json")
    st = stats(sp)
    (MAIN / "stats.json").write_text(json.dumps(st, indent=2))
    log.info("main dataset written: %s", st)


if __name__ == "__main__":
    main()
