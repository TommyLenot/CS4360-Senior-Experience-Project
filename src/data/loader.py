from pathlib import Path

import pandas as pd


NSL_KDD_COLUMNS = [
    "duration",
    "protocol_type",
    "service",
    "flag",
    "src_bytes",
    "dst_bytes",
    "land",
    "wrong_fragment",
    "urgent",
    "hot",
    "num_failed_logins",
    "logged_in",
    "num_compromised",
    "root_shell",
    "su_attempted",
    "num_root",
    "num_file_creations",
    "num_shells",
    "num_access_files",
    "num_outbound_cmds",
    "is_host_login",
    "is_guest_login",
    "count",
    "srv_count",
    "serror_rate",
    "srv_serror_rate",
    "rerror_rate",
    "srv_rerror_rate",
    "same_srv_rate",
    "diff_srv_rate",
    "srv_diff_host_rate",
    "dst_host_count",
    "dst_host_srv_count",
    "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate",
    "dst_host_srv_serror_rate",
    "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate",
    "label",
    "difficulty",
]


def load_nsl_kdd(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    data = pd.read_csv(
        file_path,
        names=NSL_KDD_COLUMNS,
        header=None
    )

    return data


if __name__ == "__main__":
    train_path = Path("data/raw/KDDTrain+.txt")
    test_path = Path("data/raw/KDDTest+.txt")

    train_data = load_nsl_kdd(train_path)
    test_data = load_nsl_kdd(test_path)

    print("Training data shape:", train_data.shape)
    print("Test data shape:", test_data.shape)

    print("\nTraining data preview:")
    print(train_data.head())