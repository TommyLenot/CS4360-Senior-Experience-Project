import json, joblib
import pandas as pd

def load_preprocessor(art="artifacts"):
    scaler = joblib.load(f"{art}/scaler.joblib")
    columns = json.load(open(f"{art}/columns.json"))
    return scaler, columns

def preprocess(df_raw, scaler, columns):
    df = df_raw.drop(columns=[c for c in ("label", "difficulty") if c in df_raw.columns])
    X = pd.get_dummies(df).reindex(columns=columns, fill_value=0).astype(float)
    return scaler.transform(X)
