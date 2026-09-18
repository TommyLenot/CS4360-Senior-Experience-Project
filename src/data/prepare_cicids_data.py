from pathlib import Path

import gc
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split

from src.data.cicids_loader import (
    get_cicids_files,
    load_cicids_file
)
from src.data.cicids_preprocessing import (
    create_preprocessor,
    separate_features_and_labels
)


OUTPUT_DIR = Path("data/processed/cicids2017")

TEST_SIZE = 0.20
RANDOM_STATE = 42


def split_file_data(data):
    train_data, test_data = train_test_split(
        data,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=data["Label"]
    )

    return train_data, test_data


def validate_raw_partition(data, partition_name):
    if data.empty:
        raise ValueError(
            f"{partition_name} partition is empty."
        )

    if "Label" not in data.columns:
        raise ValueError(
            f"{partition_name} partition is missing Label."
        )

    numeric_data = data.drop(
        columns=["Label", "source_file"],
        errors="ignore"
    )

    numeric_values = numeric_data.to_numpy()

    if not np.isfinite(numeric_values).all():
        raise ValueError(
            f"{partition_name} contains NaN or infinite values."
        )


def validate_processed_data(
    X_train_processed,
    X_test_processed,
    y_train,
    y_test
):
    if X_train_processed.shape[0] != len(y_train):
        raise ValueError(
            "Training features and labels have different row counts."
        )

    if X_test_processed.shape[0] != len(y_test):
        raise ValueError(
            "Test features and labels have different row counts."
        )

    if (
        X_train_processed.shape[1]
        != X_test_processed.shape[1]
    ):
        raise ValueError(
            "Training and test data have different feature counts."
        )

    if X_train_processed.dtype != np.float32:
        raise ValueError(
            "Training features must use float32."
        )

    if X_test_processed.dtype != np.float32:
        raise ValueError(
            "Test features must use float32."
        )

    if not np.isfinite(X_train_processed).all():
        raise ValueError(
            "Training features contain NaN or infinite values."
        )

    if not np.isfinite(X_test_processed).all():
        raise ValueError(
            "Test features contain NaN or infinite values."
        )

    valid_labels = {0, 1}

    if not set(y_train.unique()).issubset(valid_labels):
        raise ValueError(
            "Training labels must contain only 0 and 1."
        )

    if not set(y_test.unique()).issubset(valid_labels):
        raise ValueError(
            "Test labels must contain only 0 and 1."
        )


def main():
    print("Checking CICIDS2017 dataset files...")

    files = get_cicids_files()

    print(f"Found {len(files)} CICIDS2017 CSV files.")

    train_parts = []
    test_parts = []

    print("\nLoading, cleaning, and splitting files...")

    for file_path in files:
        print(f"Processing {file_path.name}...")

        data = load_cicids_file(file_path)

        data["source_file"] = file_path.name

        train_part, test_part = split_file_data(data)

        train_parts.append(train_part)
        test_parts.append(test_part)

        del data
        gc.collect()

    print("\nCombining training partitions...")

    train_data = pd.concat(
        train_parts,
        ignore_index=True
    )

    del train_parts
    gc.collect()

    print("Combining test partitions...")

    test_data = pd.concat(
        test_parts,
        ignore_index=True
    )

    del test_parts
    gc.collect()

    print("Training rows:", len(train_data))
    print("Test rows:", len(test_data))

    print("\nValidating cleaned partitions...")

    validate_raw_partition(
        train_data,
        "Training"
    )

    validate_raw_partition(
        test_data,
        "Test"
    )

    print("Cleaned partition validation passed.")

    print("\nSeparating features and labels...")

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

    del train_data
    del test_data
    gc.collect()

    print("Training input shape:", X_train.shape)
    print("Test input shape:", X_test.shape)

    print("\nFitting CICIDS2017 preprocessor...")

    preprocessor = create_preprocessor()

    X_train_processed = preprocessor.fit_transform(
        X_train
    )

    del X_train
    gc.collect()

    print("Transforming test data...")

    X_test_processed = preprocessor.transform(
        X_test
    )

    del X_test
    gc.collect()

    print("\nConverting processed data to float32...")

    X_train_processed = X_train_processed.astype(
        np.float32,
        copy=False
    )

    X_test_processed = X_test_processed.astype(
        np.float32,
        copy=False
    )

    print(
        "Processed training shape:",
        X_train_processed.shape
    )

    print(
        "Processed test shape:",
        X_test_processed.shape
    )

    print("\nValidating processed data...")

    validate_processed_data(
        X_train_processed,
        X_test_processed,
        y_train,
        y_test
    )

    print("Processed data validation passed.")

    print("\nBinary label distribution:")

    print(
        "Training:",
        y_train.value_counts().sort_index().to_dict()
    )

    print(
        "Test:",
        y_test.value_counts().sort_index().to_dict()
    )

    print("\nAttack label distribution:")

    print("Training:")
    print(attack_labels_train.value_counts())

    print("\nTest:")
    print(attack_labels_test.value_counts())

    print("\nSaving processed CICIDS2017 data...")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        X_train_processed,
        OUTPUT_DIR / "X_train_processed.joblib"
    )

    joblib.dump(
        X_test_processed,
        OUTPUT_DIR / "X_test_processed.joblib"
    )

    joblib.dump(
        y_train,
        OUTPUT_DIR / "y_train.joblib"
    )

    joblib.dump(
        y_test,
        OUTPUT_DIR / "y_test.joblib"
    )

    joblib.dump(
        attack_labels_train,
        OUTPUT_DIR / "attack_labels_train.joblib"
    )

    joblib.dump(
        attack_labels_test,
        OUTPUT_DIR / "attack_labels_test.joblib"
    )

    joblib.dump(
        preprocessor,
        OUTPUT_DIR / "preprocessor.joblib"
    )

    print(
        "Processed CICIDS2017 data saved successfully to "
        "data/processed/cicids2017/"
    )


if __name__ == "__main__":
    main()