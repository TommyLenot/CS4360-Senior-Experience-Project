import math
from typing import List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.api.datasets import get_dataset, list_datasets
from src.ingestion.result import InvestigationResult

MAX_BATCH = 10_000
DEFAULT_DATASET = "nslkdd"

app = FastAPI(title="Anomaly Detection API")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",  # Vite dev server on any local port
    allow_methods=["*"],
    allow_headers=["*"],
)

get_dataset(DEFAULT_DATASET)  # load the default dataset now so the first request is fast


def dataset_or_error(key):
    try:
        return get_dataset(key)
    except KeyError:
        raise HTTPException(404, f"unknown dataset: {key}")
    except FileNotFoundError as err:  # known dataset, but its files are not there yet
        raise HTTPException(503, str(err))


def run_demo(ds, key):
    try:
        return ds.run(key)
    except KeyError:
        raise HTTPException(404, f"unknown model: {key}")


def pick_alerts(ds, model, limit, focus):
    out = run_demo(ds, model)
    ratio = np.nan_to_num(out["ratio"], nan=0.0, posinf=1e6, neginf=0.0)
    keep = out["flagged"]
    if focus == "uncertain":
        keep = keep & ds.run_agent()[2]
    idx = np.where(keep)[0]
    idx = idx[np.argsort(-ratio[idx])][:limit]  # most suspicious first
    return idx.tolist(), ratio


def finite(x, ndigits=None):
    x = float(x)
    if not math.isfinite(x):
        return None
    return round(x, ndigits) if ndigits is not None else x


class PredictRequest(BaseModel):
    records: List[dict]  # raw rows keyed by column name; the label column is optional
    models: Optional[List[str]] = None  # model keys to run, defaults to all


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/datasets")
def datasets():
    return list_datasets()


@app.get("/models")
def list_models(dataset: str = DEFAULT_DATASET):
    ds = dataset_or_error(dataset)
    return ds.model_options()


@app.post("/predict")
def predict(req: PredictRequest, dataset: str = DEFAULT_DATASET):
    ds = dataset_or_error(dataset)
    if not req.records:
        raise HTTPException(400, "records must not be empty")
    if len(req.records) > MAX_BATCH:
        raise HTTPException(400, f"too many records (max {MAX_BATCH})")

    keys = req.models or list(ds.models)
    unknown = [k for k in keys if k not in ds.models]
    if unknown:
        raise HTTPException(400, f"unknown models: {unknown}")

    df = pd.DataFrame(req.records)
    missing = [c for c in ds.features if c not in df.columns]
    if missing:
        raise HTTPException(400, f"missing columns: {missing}")

    X = ds.preprocess(df)
    out = {k: ds.models[k].predict(X) for k in keys}
    label_col = ds.label_cols[0]  # "label" for NSL-KDD, "Label" for CICIDS2017

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
        if label_col in df.columns:
            row["label"] = str(df[label_col].iloc[i])
            row["family"] = ds.family_of(row["label"])
        results.append(row)
    return {"results": results}


@app.get("/summary")
def summary(model: str = "autoencoder", dataset: str = DEFAULT_DATASET):
    ds = dataset_or_error(dataset)
    flagged = run_demo(ds, model)["flagged"]
    tp = int((flagged & ds.is_attack).sum())
    n_flagged = int(flagged.sum())
    n_investigated = int((flagged & ds.run_agent()[2]).sum())  # flagged AND uncertain
    return {
        "dataset": ds.name,
        "rows": len(ds.demo),
        "flagged": n_flagged,
        "pending": n_flagged,
        "completed": 0,
        "investigated": n_investigated,
        "confident": n_flagged - n_investigated,
        "precision": round(tp / max(n_flagged, 1), 4),
        "recall": round(tp / max(int(ds.is_attack.sum()), 1), 4),
    }


@app.get("/alerts")
def alerts(model: str = "autoencoder", limit: int = Query(50, ge=1, le=1000),
           focus: str = "top", dataset: str = DEFAULT_DATASET):
    ds = dataset_or_error(dataset)
    idx, ratio = pick_alerts(ds, model, limit, focus)
    band = ds.run_agent()[2]
    return [
        {
            "id": f"ALT-{i:05d}",
            "type": ds.family_of(ds.labels[i]),
            "true_label": str(ds.labels[i]),
            "score": round(float(ratio[i]), 2),
            "status": "investigated" if band[i] else "confident",
        }
        for i in idx
    ]


@app.get("/traffic")
def traffic(model: str = "autoencoder", buckets: int = Query(7, ge=1, le=100),
            dataset: str = DEFAULT_DATASET):
    ds = dataset_or_error(dataset)
    flagged = run_demo(ds, model)["flagged"]
    return [
        {"time": f"Window {n + 1}", "normal": int((~part).sum()), "anomalies": int(part.sum())}
        for n, part in enumerate(np.array_split(flagged, buckets))
    ]


@app.get("/investigations")
def investigations(model: str = "autoencoder", limit: int = Query(50, ge=1, le=1000),
                   focus: str = "top", dataset: str = DEFAULT_DATASET):
    ds = dataset_or_error(dataset)
    prob, reasons, _ = ds.run_agent()
    idx, _ = pick_alerts(ds, model, limit, focus)  # same alerts, same order as /alerts
    results = []
    for i in idx:
        verdict, confidence = ds.agent.verdict(prob[i])
        results.append(
            InvestigationResult(
                alert_id=f"ALT-{i:05d}",
                verdict=verdict,
                confidence_score=confidence,
                explanation=reasons[i],
            ).to_dict()
        )
    return results
