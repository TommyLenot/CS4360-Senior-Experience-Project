import json

import joblib
import numpy as np
import pandas as pd

LABEL_COLS = ("label", "difficulty")
DETECTORS = ("isolation_forest", "mahalanobis", "autoencoder")


def to_odds(p):
    return p / (1 - p)


def to_prob(o):
    return o / (1 + o)


class Agent:
    def __init__(self, art="artifacts"):
        self.tree = joblib.load(f"{art}/agent_tree.joblib")
        self.combiner = joblib.load(f"{art}/agent_calibrator.joblib")
        self.cal = {k: joblib.load(f"{art}/calib_{k}.joblib") for k in DETECTORS}

        p = json.load(open(f"{art}/agent_params.json"))
        self.base = p["base_rate"]
        self.lr_group = {int(g): v for g, v in p["lr_group"].items()}
        self.lr_if = {}
        for key, v in p["lr_if"].items():
            leaf, flag = key.split(",")
            self.lr_if[(int(leaf), bool(int(flag)))] = v
        self.group_text = {int(g): t for g, t in p["group_text"].items()}
        self.tree_columns = p["tree_columns"]
        self.zone_low, self.zone_high = p["zone_low"], p["zone_high"]
        self.if_threshold = p["if_threshold"]
        self.escalate_at, self.review_at = p["escalate_at"], p["review_at"]

    def prior(self, scores):
        p = {}
        for k in DETECTORS:
            s = np.nan_to_num(np.asarray(scores[k], dtype=float), nan=0.0, posinf=1e12)
            p[k] = self.cal[k].predict(s)
        combined = self.combiner.predict((p["mahalanobis"] + p["autoencoder"]) / 2)
        return combined, p["isolation_forest"]

    def trace(self, leaf, if_flag):
        leaf = int(leaf)
        odds = to_odds(self.base)
        steps = [("start", 1.0, self.base)]
        odds *= self.lr_group[leaf]
        steps.append((self.group_text[leaf], self.lr_group[leaf], to_prob(odds)))
        key = (leaf, bool(if_flag))
        if key in self.lr_if:
            odds *= self.lr_if[key]
            label = "Isolation Forest says attack" if if_flag else "Isolation Forest says normal"
            steps.append((label, self.lr_if[key], to_prob(odds)))
        return steps

    def explain(self, prior_p, steps):
        lines = [f"The detectors were unsure ({prior_p:.0%} attack), so the agent checked more evidence.",
                 f"Starting point: {steps[0][2]:.0%} of similar uncertain records were attacks"]
        lines += [f"{label}: attack {'more' if ratio > 1 else 'less'} likely (odds x{ratio:.2f}) -> {prob:.0%}"
                  for label, ratio, prob in steps[1:]]
        return " | ".join(lines)

    def verdict(self, p):
        if p >= self.escalate_at: return "malicious", float(p)
        if p >= self.review_at: return "suspicious", float(p)
        return "benign", float(1 - p)
    
    
    def investigate(self, df_raw, scores):
        prior, p_if = self.prior(scores)
        prob = prior.copy()
        reasons = [None] * len(prior)
        in_band = (prior > self.zone_low) & (prior < self.zone_high)
        if in_band.any():
            raw = df_raw[in_band]
            drop = [c for c in LABEL_COLS if c in raw.columns]
            feats = (pd.get_dummies(raw.drop(columns=drop))
                       .reindex(columns=self.tree_columns, fill_value=0).astype(float))
            leaves = self.tree.apply(feats)
            if_flags = p_if[in_band] > self.if_threshold
            for pos, i in enumerate(np.where(in_band)[0]):
                steps = self.trace(leaves[pos], if_flags[pos])
                prob[i] = np.clip(steps[-1][2], 0.001, 0.999)
                reasons[i] = self.explain(prior[i], steps)
        for i in np.where(~in_band)[0]:
            reasons[i] = (f"Mahalanobis and the autoencoder together put this record at "
                          f"{prior[i]:.0%} attack, outside the uncertain band "
                          f"({self.zone_low:.0%} to {self.zone_high:.0%}), "
                          f"so no extra evidence was needed.")
        return prob, reasons
    