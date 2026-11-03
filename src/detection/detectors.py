import json
import joblib
import numpy as np
import torch
import torch.nn as nn


class Autoencoder(nn.Module):  # nn.Module means inherits PyTorch base model class
    def __init__(self, n_features=122, bottleneck=16):  # self means this particular autoencoder
        super().__init__()  # runs parent class setup, PyTorch needs nn.Module first
        self.encoder = nn.Sequential(  # chains layers in order
            nn.Linear(n_features, 64), nn.ReLU(),  # takes 122 numbers and produces 64
            nn.Linear(64, 32), nn.ReLU(),  # nn.ReLU() replaces negative numbers with 0
            nn.Linear(32, bottleneck),  # squeezes to 16 numbers, bottleneck is the compression
        )
        self.decoder = nn.Sequential(  # mirror image: 16 to 32 to 64 to 122, rebuilds the original input
            nn.Linear(bottleneck, 32), nn.ReLU(),
            nn.Linear(32, 64), nn.ReLU(),
            nn.Linear(64, n_features),
        )

    def forward(self, x):  # forward defines what happens when you call model(x)
        return self.decoder(self.encoder(x))


class Detector:
    name = ""

    def __init__(self, threshold):
        self.threshold = threshold

    def score(self, X):
        raise NotImplementedError

    def predict(self, X):
        s = self.score(X)
        return {"score": s, "flagged": s > self.threshold, "ratio": s / self.threshold}


class IsoForest(Detector):
    name = "Isolation Forest"

    def __init__(self, model, threshold):
        super().__init__(threshold)
        self.model = model

    def score(self, X):
        return -self.model.score_samples(X)


class Mahalanobis(Detector):
    name = "Mahalanobis"

    def __init__(self, mu, cov_inv, threshold):
        super().__init__(threshold)
        self.mu = mu
        self.cov_inv = cov_inv

    def score(self, X):
        d = X - self.mu
        return ((d @ self.cov_inv) * d).sum(axis=1)


class AE(Detector):
    name = "Autoencoder"

    def __init__(self, model, threshold):
        super().__init__(threshold)
        self.model = model.eval()

    def score(self, X):
        with torch.no_grad():
            t = torch.tensor(X, dtype=torch.float32)
            return ((self.model(t) - t) ** 2).mean(dim=1).numpy()


class LogReg(Detector):
    def __init__(self, model, name, threshold=0.5):
        super().__init__(threshold)
        self.model = model
        self.name = name

    def score(self, X):
        return self.model.predict_proba(X)[:, 1]


def load_all(art="artifacts"):
    th = json.load(open(f"{art}/thresholds.json"))
    z = np.load(f"{art}/mahalanobis.npz")

    ae = Autoencoder(n_features=z["mu"].shape[0], bottleneck=16)
    ae.load_state_dict(torch.load(f"{art}/autoencoder.pt", map_location="cpu"))

    models = {
        "autoencoder": AE(ae, th["autoencoder"]),
        "mahalanobis": Mahalanobis(z["mu"], z["cov_inv"], th["mahalanobis"]),
        "isolation_forest": IsoForest(joblib.load(f"{art}/iso_forest.joblib"), th["isolation_forest"]),
    }

    for pct in (5, 1):
        for kind, label in (("baseline", "Baseline"), ("selftrained", "Self-trained")):
            key = f"lr_{kind}_{pct}"
            models[key] = LogReg(
                joblib.load(f"{art}/{key}.joblib"),
                f"Logistic Regression, {label} ({pct}% labels)",
                th["logreg"],
            )
    return models
