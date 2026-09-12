import pandas as pd

from src.data.preprocessing import (
    separate_features_and_labels,
    preprocess_train_test
)


def test_separate_features_and_labels():
    data = pd.DataFrame({
        "protocol_type": ["tcp", "udp"],
        "service": ["http", "domain_u"],
        "flag": ["SF", "SF"],
        "duration": [0, 5],
        "src_bytes": [100, 200],
        "label": ["normal", "neptune"],
        "difficulty": [20, 15]
    })

    X, y = separate_features_and_labels(data)

    assert "label" not in X.columns
    assert "difficulty" not in X.columns
    assert y.tolist() == [0, 1]


def test_preprocess_train_test():
    train_data = pd.DataFrame({
        "protocol_type": ["tcp", "udp", "tcp"],
        "service": ["http", "domain_u", "ftp"],
        "flag": ["SF", "SF", "REJ"],
        "duration": [0, 5, 10],
        "src_bytes": [100, 200, 300],
        "label": ["normal", "neptune", "normal"],
        "difficulty": [20, 15, 18]
    })

    test_data = pd.DataFrame({
        "protocol_type": ["tcp", "icmp"],
        "service": ["http", "eco_i"],
        "flag": ["SF", "SF"],
        "duration": [2, 8],
        "src_bytes": [150, 250],
        "label": ["normal", "smurf"],
        "difficulty": [19, 17]
    })

    (
        X_train_processed,
        X_test_processed,
        y_train,
        y_test,
        preprocessor
    ) = preprocess_train_test(train_data, test_data)

    assert X_train_processed.shape[0] == 3
    assert X_test_processed.shape[0] == 2
    assert X_train_processed.shape[1] == X_test_processed.shape[1]

    assert y_train.tolist() == [0, 1, 0]
    assert y_test.tolist() == [0, 1]