import math
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.detection.columns import COLUMNS, FEATURES, family
from src.detection.preprocess import load_preprocessor, preprocess
from src.detection.detectors import load_all
from src.detection.agent import Agent, DETECTORS
from src.ingestion.result import InvestigationResult

ROOT = Path(__file__).resolve().parents[2]  # repo root
ART = str(ROOT / "artifacts")
DEMO_PATH = ROOT / "data" / "raw" / "KDDTest+.txt"
MAX_BATCH = 10_000

app = FastAPI(title="Anomaly Detection API")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",  # Vite dev server on any local port
    allow_methods=["*"],
    allow_headers=["*"],
)

scaler, columns = load_preprocessor(ART)
models = load_all(ART)

# replay data for the dashboard, scored once per model and cached
demo = pd.read_csv(DEMO_PATH, header=None, names=COLUMNS)
X_demo = preprocess(demo, scaler, columns)
is_attack = (demo["label"] != "normal").to_numpy()
_cache = {}
agent = Agent(ART)
_agent_cache = {}


def run_demo(key):
    if key not in models:
        raise HTTPException(404, f"unknown model: {key}")
    if key not in _cache:
        _cache[key] = models[key].predict(X_demo)
    return _cache[key]


def finite(x, ndigits=None):
    x = float(x)
    if not math.isfinite(x):
        return None
    return round(x, ndigits) if ndigits is not None else x


class PredictRequest(BaseModel):
    records: List[dict]  # raw NSL-KDD rows keyed by column name; "label" is optional
    models: Optional[List[str]] = None  # model keys to run, defaults to all


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/models")
def list_models():
    return [
        {
            "key": k,
            "name": m.name,
            "threshold": float(m.threshold),
            "family": "Label scarcity" if k.startswith("lr_") else "Anomaly detector",
        }
        for k, m in models.items()
    ]


@app.post("/predict")
def predict(req: PredictRequest):
    if not req.records:
        raise HTTPException(400, "records must not be empty")
    if len(req.records) > MAX_BATCH:
        raise HTTPException(400, f"too many records (max {MAX_BATCH})")

    keys = req.models or list(models)
    unknown = [k for k in keys if k not in models]
    if unknown:
        raise HTTPException(400, f"unknown models: {unknown}")

    df = pd.DataFrame(req.records)
    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise HTTPException(400, f"missing columns: {missing}")

    X = preprocess(df, scaler, columns)
    out = {k: models[k].predict(X) for k in keys}

    results = []
    for i in range(len(df)):
        row = {
            "index": i,
            "models": {
                k: {
                    "score": finite(out[k]["score"][i]),
                    "flagged": bool(out[k]["flagged"][i]),
                    "ratio": finite(out[k]["ratio"][i]),
                }
                for k in keys
            },
        }
        if "label" in df.columns:
            row["label"] = str(df["label"].iloc[i])
            row["family"] = family(row["label"])
        results.append(row)
    return {"results": results}


@app.get("/summary")
def summary(model: str = "autoencoder"):
    flagged = run_demo(model)["flagged"]
    tp = int((flagged & is_attack).sum())
    n_flagged = int(flagged.sum())
    n_investigated = int((flagged & run_agent()[2]).sum())  # flagged AND uncertain
    return {
        "rows": len(demo),
        "flagged": n_flagged,
        "pending": n_flagged,
        "completed": 0,
        "investigated": n_investigated,
        "confident": n_flagged - n_investigated,
        "precision": round(tp / max(n_flagged, 1), 4),
        "recall": round(tp / int(is_attack.sum()), 4),
    }


@app.get("/traffic")
def traffic(model: str = "autoencoder", buckets: int = Query(7, ge=1, le=100)):
    flagged = run_demo(model)["flagged"]
    return [
        {"time": f"Window {n + 1}", "normal": int((~part).sum()), "anomalies": int(part.sum())}
        for n, part in enumerate(np.array_split(flagged, buckets))
    ]


def run_agent():
    # the agent reads Mahalanobis + autoencoder + Isolation Forest scores for every demo row, once
    if "out" not in _agent_cache:
        scores = {k: run_demo(k)["score"] for k in DETECTORS}
        prior, _ = agent.prior(scores)
        band = (prior > agent.zone_low) & (prior < agent.zone_high)  # the uncertain rows
        prob, reasons = agent.investigate(demo, scores)
        _agent_cache["out"] = (prob, reasons, band)
    return _agent_cache["out"]


def pick_alerts(model, limit, focus):
    out = run_demo(model)
    ratio = np.nan_to_num(out["ratio"], nan=0.0, posinf=1e6, neginf=0.0)
    keep = out["flagged"]
    if focus == "uncertain":
        keep = keep & run_agent()[2]
    idx = np.where(keep)[0]
    idx = idx[np.argsort(-ratio[idx])][:limit]  # most suspicious first
    return idx.tolist(), ratio


@app.get("/alerts")
def alerts(model: str = "autoencoder", limit: int = Query(50, ge=1, le=1000), focus: str = "top"):
    idx, ratio = pick_alerts(model, limit, focus)
    band = run_agent()[2]
    return [
        {
            "id": f"ALT-{i:05d}",
            "type": family(demo.at[i, "label"]),
            "true_label": demo.at[i, "label"],
            "score": round(float(ratio[i]), 2),
            "status": "investigated" if band[i] else "confident",
        }
        for i in idx
    ]


@app.get("/investigations")
def investigations(model: str = "autoencoder", limit: int = Query(50, ge=1, le=1000), focus: str = "top"):
    prob, reasons, _ = run_agent()
    idx, _ = pick_alerts(model, limit, focus)  # same alerts, same order as /alerts
    results = []
    for i in idx:
        verdict, confidence = agent.verdict(prob[i])
        results.append(
            InvestigationResult(
                alert_id=f"ALT-{i:05d}",
                verdict=verdict,
                confidence_score=confidence,
                explanation=reasons[i],
            ).to_dict()
        )
    return results
