import numpy as np
import pandas as pd
import pytest

from src.data.prepare_data import validate_processed_data


def test_valid_processed_data():
    X_train = np.zeros((3, 5))
    X_test = np.zeros((2, 5))

    y_train = pd.Series([0, 1, 0])
    y_test = pd.Series([0, 1])

    validate_processed_data(
        X_train,
        X_test,
        y_train,
        y_test
    )


def test_training_row_mismatch():
    X_train = np.zeros((3, 5))
    X_test = np.zeros((2, 5))

    y_train = pd.Series([0, 1])
    y_test = pd.Series([0, 1])

    with pytest.raises(
        ValueError,
        match="Training features and training labels"
    ):
        validate_processed_data(
            X_train,
            X_test,
            y_train,
            y_test
        )


def test_test_row_mismatch():
    X_train = np.zeros((3, 5))
    X_test = np.zeros((2, 5))

    y_train = pd.Series([0, 1, 0])
    y_test = pd.Series([0])

    with pytest.raises(
        ValueError,
        match="Test features and test labels"
    ):
        validate_processed_data(
            X_train,
            X_test,
            y_train,
            y_test
        )


def test_feature_count_mismatch():
    X_train = np.zeros((3, 5))
    X_test = np.zeros((2, 4))

    y_train = pd.Series([0, 1, 0])
    y_test = pd.Series([0, 1])

    with pytest.raises(
        ValueError,
        match="different feature counts"
    ):
        validate_processed_data(
            X_train,
            X_test,
            y_train,
            y_test
        )


def test_training_nan_rejected():
    X_train = np.zeros((3, 5))
    X_train[0, 0] = np.nan

    X_test = np.zeros((2, 5))

    y_train = pd.Series([0, 1, 0])
    y_test = pd.Series([0, 1])

    with pytest.raises(
        ValueError,
        match="Training features contain NaN or infinite values"
    ):
        validate_processed_data(
            X_train,
            X_test,
            y_train,
            y_test
        )


def test_test_infinity_rejected():
    X_train = np.zeros((3, 5))

    X_test = np.zeros((2, 5))
    X_test[0, 0] = np.inf

    y_train = pd.Series([0, 1, 0])
    y_test = pd.Series([0, 1])

    with pytest.raises(
        ValueError,
        match="Test features contain NaN or infinite values"
    ):
        validate_processed_data(
            X_train,
            X_test,
            y_train,
            y_test
        )


def test_invalid_training_labels_rejected():
    X_train = np.zeros((3, 5))
    X_test = np.zeros((2, 5))

    y_train = pd.Series([0, 2, 0])
    y_test = pd.Series([0, 1])

    with pytest.raises(
        ValueError,
        match="Training labels must contain only 0 and 1"
    ):
        validate_processed_data(
            X_train,
            X_test,
            y_train,
            y_test
        )


def test_invalid_test_labels_rejected():
    X_train = np.zeros((3, 5))
    X_test = np.zeros((2, 5))

    y_train = pd.Series([0, 1, 0])
    y_test = pd.Series([0, 3])

    with pytest.raises(
        ValueError,
        match="Test labels must contain only 0 and 1"
    ):
        validate_processed_data(
            X_train,
            X_test,
            y_train,
            y_test
        )