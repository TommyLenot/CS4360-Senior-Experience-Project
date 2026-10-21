from pathlib import Path
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.feature_selection import VarianceThreshold
from sklearn.pipeline import Pipeline
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

    column_transformer = ColumnTransformer(
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

    preprocessor = Pipeline(
        steps=[
            ("column_transformer", column_transformer),
            ("variance_filter", VarianceThreshold(threshold=0.0))
        ]
    )

    return preprocessor


def preprocess_train_test(train_data, test_data):
    X_train, y_train = separate_features_and_labels(train_data)
    X_test, y_test = separate_features_and_labels(test_data)

    preprocessor = create_preprocessor(X_train)

    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    return (
        X_train_processed,
        X_test_processed,
        y_train,
        y_test,
        preprocessor
    )


def save_processed_data(
    X_train_processed,
    X_test_processed,
    y_train,
    y_test,
    preprocessor,
    output_dir="data/processed"
):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

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
        preprocessor,
        output_path / "preprocessor.joblib"
    )


def load_processed_data(output_dir="data/processed"):
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

    preprocessor = joblib.load(
        output_path / "preprocessor.joblib"
    )

    return (
        X_train_processed,
        X_test_processed,
        y_train,
        y_test,
        preprocessor
    )