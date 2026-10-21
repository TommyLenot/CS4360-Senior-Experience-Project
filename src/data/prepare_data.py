from pathlib import Path

import numpy as np

from src.data.loader import load_nsl_kdd
from src.data.preprocessing import (
    preprocess_train_test,
    save_processed_data
)


TRAIN_PATH = Path("data/raw/KDDTrain+.txt")
TEST_PATH = Path("data/raw/KDDTest+.txt")


def validate_raw_files():
    missing_files = []

    if not TRAIN_PATH.exists():
        missing_files.append(str(TRAIN_PATH))

    if not TEST_PATH.exists():
        missing_files.append(str(TEST_PATH))

    if missing_files:
        print("ERROR: Required NSL-KDD dataset files are missing.")

        for file_path in missing_files:
            print(f"Missing: {file_path}")

        print(
            "\nDownload KDDTrain+.txt and KDDTest+.txt "
            "and place them in data/raw/."
        )

        return False

    return True


def validate_processed_data(
    X_train_processed,
    X_test_processed,
    y_train,
    y_test
):
    if X_train_processed.shape[0] != len(y_train):
        raise ValueError(
            "Training features and training labels have different row counts."
        )

    if X_test_processed.shape[0] != len(y_test):
        raise ValueError(
            "Test features and test labels have different row counts."
        )

    if X_train_processed.shape[1] != X_test_processed.shape[1]:
        raise ValueError(
            "Training and test data have different feature counts."
        )

    if not np.issubdtype(X_train_processed.dtype, np.number):
        raise ValueError(
            "Training features must contain numeric data."
        )

    if not np.issubdtype(X_test_processed.dtype, np.number):
        raise ValueError(
            "Test features must contain numeric data."
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
    print("Checking NSL-KDD dataset files...")

    if not validate_raw_files():
        return

    print("Dataset files found.")

    print("\nLoading NSL-KDD data...")

    train_data = load_nsl_kdd(TRAIN_PATH)
    test_data = load_nsl_kdd(TEST_PATH)

    print("Training shape:", train_data.shape)
    print("Test shape:", test_data.shape)

    print("\nPreprocessing data...")

    (
        X_train_processed,
        X_test_processed,
        y_train,
        y_test,
        preprocessor
    ) = preprocess_train_test(train_data, test_data)

    print("Processed training shape:", X_train_processed.shape)
    print("Processed test shape:", X_test_processed.shape)

    print("\nValidating processed data...")

    validate_processed_data(
        X_train_processed,
        X_test_processed,
        y_train,
        y_test
    )

    print("Processed data validation passed.")

    print("\nSaving processed data...")

    save_processed_data(
        X_train_processed,
        X_test_processed,
        y_train,
        y_test,
        preprocessor
    )

    print("Processed data saved successfully to data/processed/")


if __name__ == "__main__":
    main()