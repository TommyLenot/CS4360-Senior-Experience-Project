from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_CICIDS_DIR = Path(
    "data/raw/cicids2017/MachineLearningCVE"
)


def clean_column_names(data):
    data = data.copy()
    data.columns = data.columns.str.strip()

    return data


def clean_labels(data):
    data = data.copy()

    if "Label" not in data.columns:
        raise ValueError(
            "CICIDS2017 data does not contain a Label column."
        )

    data["Label"] = (
        data["Label"]
        .astype(str)
        .str.strip()
        .str.replace("�", "-", regex=False)
    )

    return data


def clean_invalid_values(data):
    data = data.copy()

    data.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    rows_before = len(data)

    data.dropna(
        subset=["Flow Bytes/s", "Flow Packets/s"],
        inplace=True
    )

    rows_removed = rows_before - len(data)

    return data, rows_removed


def load_cicids_file(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"CICIDS2017 file not found: {file_path}"
        )

    data = pd.read_csv(file_path)

    data = clean_column_names(data)
    data = clean_labels(data)
    data, _ = clean_invalid_values(data)

    return data


def get_cicids_files(
    data_dir=DEFAULT_CICIDS_DIR
):
    data_dir = Path(data_dir)

    if not data_dir.exists():
        raise FileNotFoundError(
            f"CICIDS2017 directory not found: {data_dir}"
        )

    files = sorted(data_dir.glob("*.csv"))

    if not files:
        raise FileNotFoundError(
            f"No CICIDS2017 CSV files found in: {data_dir}"
        )

    return files


def load_cicids2017(
    data_dir=DEFAULT_CICIDS_DIR
):
    files = get_cicids_files(data_dir)

    datasets = []

    for file_path in files:
        print(f"Loading {file_path.name}...")

        data = load_cicids_file(file_path)

        data["source_file"] = file_path.name

        datasets.append(data)

    combined_data = pd.concat(
        datasets,
        ignore_index=True
    )

    return combined_data


if __name__ == "__main__":
    data = load_cicids2017()

    print("\nCICIDS2017 loaded successfully.")
    print("Shape:", data.shape)

    print("\nLabels:")
    print(data["Label"].value_counts())

    print("\nDestination Port available:")
    print("Destination Port" in data.columns)