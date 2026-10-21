from pathlib import Path

import joblib
import numpy as np

from sklearn.feature_selection import VarianceThreshold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def separate_features_and_labels(data):
    X = data.drop(
        columns=["Label", "source_file"],
        errors="ignore"
    )

    attack_labels = data["Label"].copy()

    binary_labels = data["Label"].apply(
        lambda value: 0 if value == "BENIGN" else 1
    )

    return X, binary_labels, attack_labels


def create_preprocessor():
    preprocessor = Pipeline(
        steps=[
            (
                "variance_filter",
                VarianceThreshold(threshold=0.0)
            ),
            (
                "scaler",
                StandardScaler()
            )
        ]
    )

    return preprocessor


def preprocess_train_test(
    train_data,
    test_data
):
    (
        X_train,
        y_train,
        attack_labels_train
    ) = separate_features_and_labels(train_data)

    (
        X_test,
        y_test,
        attack_labels_test
    ) = separate_features_and_labels(test_data)

    preprocessor = create_preprocessor()

    X_train_processed = preprocessor.fit_transform(
        X_train
    )

    X_test_processed = preprocessor.transform(
        X_test
    )

    X_train_processed = X_train_processed.astype(
        np.float32,
        copy=False
    )

    X_test_processed = X_test_processed.astype(
        np.float32,
        copy=False
    )

    return (
        X_train_processed,
        X_test_processed,
        y_train,
        y_test,
        attack_labels_train,
        attack_labels_test,
        preprocessor
    )


def save_processed_data(
    X_train_processed,
    X_test_processed,
    y_train,
    y_test,
    attack_labels_train,
    attack_labels_test,
    preprocessor,
    output_dir="data/processed/cicids2017"
):
    output_path = Path(output_dir)
    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        X_train_processed,
        output_path / "X_train_processed.joblib"
    )

    joblib.dump(
        X_test_processed,
        output_path / "X_test_processed.joblib"
    )

    joblib.dump(
        y_train,
        output_path / "y_train.joblib"
    )

    joblib.dump(
        y_test,
        output_path / "y_test.joblib"
    )

    joblib.dump(
        attack_labels_train,
        output_path / "attack_labels_train.joblib"
    )

    joblib.dump(
        attack_labels_test,
        output_path / "attack_labels_test.joblib"
    )

    joblib.dump(
        preprocessor,
        output_path / "preprocessor.joblib"
    )


def load_processed_data(
    output_dir="data/processed/cicids2017"
):
    output_path = Path(output_dir)

    X_train_processed = joblib.load(
        output_path / "X_train_processed.joblib"
    )

    X_test_processed = joblib.load(
        output_path / "X_test_processed.joblib"
    )

    y_train = joblib.load(
        output_path / "y_train.joblib"
    )

    y_test = joblib.load(
        output_path / "y_test.joblib"
    )

    attack_labels_train = joblib.load(
        output_path / "attack_labels_train.joblib"
    )

    attack_labels_test = joblib.load(
        output_path / "attack_labels_test.joblib"
    )

    preprocessor = joblib.load(
        output_path / "preprocessor.joblib"
    )

    return (
        X_train_processed,
        X_test_processed,
        y_train,
        y_test,
        attack_labels_train,
        attack_labels_test,
        preprocessor
    )