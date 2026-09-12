import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler


CATEGORICAL_COLUMNS = [
    "protocol_type",
    "service",
    "flag"
]


def separate_features_and_labels(data):
    X = data.drop(columns=["label", "difficulty"])
    y = data["label"].apply(lambda value: 0 if value == "normal" else 1)

    return X, y


def get_numerical_columns(data):
    return [
        column
        for column in data.columns
        if column not in CATEGORICAL_COLUMNS
    ]


def create_preprocessor(data):
    numerical_columns = get_numerical_columns(data)

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_COLUMNS
            ),
            (
                "numerical",
                StandardScaler(),
                numerical_columns
            )
        ]
    )

    return preprocessor