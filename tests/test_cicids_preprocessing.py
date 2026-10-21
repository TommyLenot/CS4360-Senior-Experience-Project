import numpy as np
import pandas as pd

from src.data.cicids_preprocessing import (
    create_preprocessor,
    preprocess_train_test,
    separate_features_and_labels
)


def create_sample_data():
    return pd.DataFrame(
        {
            "Destination Port": [
                80,
                443,
                22,
                21,
                8080,
                53
            ],
            "Flow Duration": [
                1000,
                2000,
                3000,
                4000,
                5000,
                6000
            ],
            "Total Fwd Packets": [
                5,
                10,
                15,
                20,
                25,
                30
            ],
            "Constant Feature": [
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "Label": [
                "BENIGN",
                "DDoS",
                "BENIGN",
                "PortScan",
                "BENIGN",
                "DoS Hulk"
            ],
            "source_file": [
                "sample.csv",
                "sample.csv",
                "sample.csv",
                "sample.csv",
                "sample.csv",
                "sample.csv"
            ]
        }
    )


def test_separate_features_and_labels():
    data = create_sample_data()

    X, binary_labels, attack_labels = (
        separate_features_and_labels(data)
    )

    assert "Label" not in X.columns
    assert "source_file" not in X.columns

    assert list(binary_labels) == [
        0,
        1,
        0,
        1,
        0,
        1
    ]

    assert list(attack_labels) == [
        "BENIGN",
        "DDoS",
        "BENIGN",
        "PortScan",
        "BENIGN",
        "DoS Hulk"
    ]


def test_preprocessor_removes_constant_features():
    data = create_sample_data()

    X, _, _ = separate_features_and_labels(data)

    preprocessor = create_preprocessor()

    processed = preprocessor.fit_transform(X)

    assert processed.shape == (6, 3)


def test_preprocess_train_test_shapes_match():
    train_data = create_sample_data()
    test_data = create_sample_data()

    (
        X_train_processed,
        X_test_processed,
        y_train,
        y_test,
        attack_labels_train,
        attack_labels_test,
        _
    ) = preprocess_train_test(
        train_data,
        test_data
    )

    assert X_train_processed.shape == (6, 3)
    assert X_test_processed.shape == (6, 3)

    assert len(y_train) == 6
    assert len(y_test) == 6

    assert len(attack_labels_train) == 6
    assert len(attack_labels_test) == 6


def test_processed_data_uses_float32():
    train_data = create_sample_data()
    test_data = create_sample_data()

    (
        X_train_processed,
        X_test_processed,
        _,
        _,
        _,
        _,
        _
    ) = preprocess_train_test(
        train_data,
        test_data
    )

    assert X_train_processed.dtype == np.float32
    assert X_test_processed.dtype == np.float32


def test_processed_data_is_finite():
    train_data = create_sample_data()
    test_data = create_sample_data()

    (
        X_train_processed,
        X_test_processed,
        _,
        _,
        _,
        _,
        _
    ) = preprocess_train_test(
        train_data,
        test_data
    )

    assert np.isfinite(X_train_processed).all()
    assert np.isfinite(X_test_processed).all()


def test_binary_labels_only_contain_zero_and_one():
    train_data = create_sample_data()
    test_data = create_sample_data()

    (
        _,
        _,
        y_train,
        y_test,
        _,
        _,
        _
    ) = preprocess_train_test(
        train_data,
        test_data
    )

    assert set(y_train.unique()).issubset({0, 1})
    assert set(y_test.unique()).issubset({0, 1})