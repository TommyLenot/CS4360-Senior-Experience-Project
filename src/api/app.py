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
    return {
        "rows": len(demo),
        "flagged": n_flagged,
        "pending": n_flagged,
        "completed": 0,
        "precision": round(tp / max(n_flagged, 1), 4),
        "recall": round(tp / int(is_attack.sum()), 4),
    }


@app.get("/alerts")
def alerts(model: str = "autoencoder", limit: int = Query(50, ge=1, le=1000)):
    out = run_demo(model)
    ratio = np.nan_to_num(out["ratio"], nan=0.0, posinf=1e6, neginf=0.0)
    idx = np.where(out["flagged"])[0]
    idx = idx[np.argsort(-ratio[idx])][:limit]  # most suspicious first
    return [
        {
            "id": f"ALT-{i:05d}",
            "type": family(demo.at[i, "label"]),
            "true_label": demo.at[i, "label"],
            "score": round(float(ratio[i]), 2),
            "status": "pending",
        }
        for i in idx.tolist()
    ]


@app.get("/traffic")
def traffic(model: str = "autoencoder", buckets: int = Query(7, ge=1, le=100)):
    flagged = run_demo(model)["flagged"]
    return [
        {"time": f"Window {n + 1}", "normal": int((~part).sum()), "anomalies": int(part.sum())}
        for n, part in enumerate(np.array_split(flagged, buckets))
    ]


@app.get("/investigations")
def investigations():
    return []  # filled in when the agent exists