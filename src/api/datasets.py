"""The datasets the dashboard can switch between.

Each dataset bundles everything the API needs to score and investigate it:
the detectors, the agent, the replay rows, and how to name attack families.
Datasets are built the first time they are asked for, then kept in memory.
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.detection.agent import Agent, DETECTORS
from src.detection.columns import COLUMNS, FEATURES, family as nslkdd_family
from src.detection.detectors import load_all
from src.detection.preprocess import load_preprocessor, preprocess as nslkdd_preprocess

ROOT = Path(__file__).resolve().parents[2]  # repo root


class Dataset:
    def __init__(self, key, name, art, demo, labels, benign_label, family_of,
                 label_cols, features, preprocess, agent_model=False):
        self.key = key
        self.name = name
        self.art = str(art)
        self.models = load_all(self.art)
        self.agent = Agent(self.art)
        self.demo = demo                      # raw replay rows (with their label columns)
        self.labels = np.asarray(labels)      # attack name per row, e.g. "neptune" or "DoS Hulk"
        self.is_attack = np.array([str(x).strip().lower() != benign_label for x in self.labels])
        self.family_of = family_of
        self.label_cols = [c for c in label_cols if c in demo.columns]
        self.features = list(features)        # raw columns /predict must receive
        self.preprocess = preprocess          # raw DataFrame -> matrix the detectors score
        self.X = preprocess(demo)
        self._scores = {}
        self._agent_out = None
        self.agent_model = agent_model        # True: the dashboard also offers the agent as a model

    def model_options(self):
        options = [
            {"key": k, "name": m.name, "threshold": float(m.threshold),
             "family": "Label scarcity" if k.startswith("lr_") else "Anomaly detector"}
            for k, m in self.models.items()
        ]
        if self.agent_model:  # the agent goes first: it is the best of them
            options.insert(0, {"key": "agent", "name": "Agent", "threshold": float(self.agent.review_at),
                               "family": "Agent"})
        return options

    def run(self, model_key):
        if self.agent_model and model_key == "agent":
            prob = self.run_agent()[0]  # the agent's attack probability for every replay row
            cut = self.agent.review_at  # at or above this the agent sends the alert to a human
            return {"score": prob, "flagged": prob >= cut, "ratio": prob / cut}
        if model_key not in self.models:
            raise KeyError(model_key)
        if model_key not in self._scores:
            self._scores[model_key] = self.models[model_key].predict(self.X)
        return self._scores[model_key]

    def run_agent(self):
        # the agent reads all three detectors' scores for every replay row, once
        if self._agent_out is None:
            scores = {k: self.run(k)["score"] for k in DETECTORS}
            prior, _ = self.agent.prior(scores)
            band = (prior > self.agent.zone_low) & (prior < self.agent.zone_high)  # uncertain rows
            raw = self.demo.drop(columns=self.label_cols)  # the agent must never see the answer
            prob, reasons = self.agent.investigate(raw, scores)
            self._agent_out = (prob, reasons, band)
        return self._agent_out


# ---------------------------------------------------------------- NSL-KDD
def _nslkdd_ready():
    art = ROOT / "artifacts"
    needed = [art / "scaler.joblib", art / "agent_params.json", ROOT / "data" / "raw" / "KDDTest+.txt"]
    missing = [p.name for p in needed if not p.exists()]
    return (not missing), (f"missing: {', '.join(missing)}" if missing else "")


def _build_nslkdd():
    art = ROOT / "artifacts"
    scaler, columns = load_preprocessor(str(art))
    demo = pd.read_csv(ROOT / "data" / "raw" / "KDDTest+.txt", header=None, names=COLUMNS)
    return Dataset(
        key="nslkdd", name="NSL-KDD", art=art, demo=demo,
        labels=demo["label"], benign_label="normal", family_of=nslkdd_family,
        label_cols=("label", "difficulty"), features=FEATURES,
        preprocess=lambda df: nslkdd_preprocess(df, scaler, columns),
    )


# ---------------------------------------------------------------- CICIDS2017
CICIDS_DIR = ROOT / "artifacts" / "cicids2017"
CICIDS_LABEL = "Label"
CICIDS_DROP = ("Label", "source_file")

CICIDS_FAMILIES = {
    "DoS": ["dos hulk", "dos goldeneye", "dos slowloris", "dos slowhttptest", "ddos"],
    "Probe": ["portscan"],
    "Brute force": ["ftp-patator", "ssh-patator"],
    "Web attack": ["web attack - brute force", "web attack - xss", "web attack - sql injection"],
    "Botnet": ["bot"],
    "Infiltration": ["infiltration"],
    "Exploit": ["heartbleed"],
}
_CICIDS_TO_FAMILY = {lab: fam for fam, labs in CICIDS_FAMILIES.items() for lab in labs}


def cicids_family(label):
    label = str(label).strip().lower()
    if label == "benign":
        return "normal"
    return _CICIDS_TO_FAMILY.get(label, "unknown")


def _cicids_ready():
    needed = ["preprocessor.joblib", "demo.csv.gz", "agent_params.json", "thresholds.json",
              "mahalanobis.npz", "autoencoder.pt", "iso_forest.joblib"]
    missing = [n for n in needed if not (CICIDS_DIR / n).exists()]
    return (not missing), (f"missing in artifacts/cicids2017: {', '.join(missing)}" if missing else "")


def _build_cicids():
    pipeline = joblib.load(CICIDS_DIR / "preprocessor.joblib")
    demo = pd.read_csv(CICIDS_DIR / "demo.csv.gz")
    features = [c for c in demo.columns if c not in CICIDS_DROP]

    def preprocess(df):
        return pipeline.transform(df[features]).astype(np.float32)

    return Dataset(
        key="cicids2017", name="CICIDS2017", art=CICIDS_DIR, demo=demo,
        labels=demo[CICIDS_LABEL], benign_label="benign", family_of=cicids_family,
        label_cols=CICIDS_DROP, features=features, preprocess=preprocess,
        agent_model=True,
    )


# ---------------------------------------------------------------- registry
REGISTRY = {
    "nslkdd": ("NSL-KDD", _nslkdd_ready, _build_nslkdd, "autoencoder"),
    "cicids2017": ("CICIDS2017", _cicids_ready, _build_cicids, "agent"),
}
_loaded = {}


def list_datasets():
    out = []
    for key, (name, ready_fn, _, default_model) in REGISTRY.items():
        ready, reason = ready_fn()
        out.append({"key": key, "name": name, "ready": ready, "reason": reason, "default_model": default_model})
    return out


def get_dataset(key):
    """Return the built dataset. Raises KeyError (unknown) or FileNotFoundError (not set up yet)."""
    if key not in REGISTRY:
        raise KeyError(key)
    if key not in _loaded:
        name, ready_fn, build, _ = REGISTRY[key]
        ready, reason = ready_fn()
        if not ready:
            raise FileNotFoundError(f"{name} is not set up yet ({reason})")
        _loaded[key] = build()
    return _loaded[key]
