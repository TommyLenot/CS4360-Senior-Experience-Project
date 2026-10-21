from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from src.data.preprocessing import load_processed_data


def test_processed_data_works_with_logistic_regression():
    (
        X_train,
        X_test,
        y_train,
        y_test,
        _
    ) = load_processed_data()

    # Use a small sample so this remains a compatibility test
    # rather than performing the team's actual Week 3 model comparison.
    sample_size = 1000

    X_train_sample = X_train[:sample_size]
    y_train_sample = y_train.iloc[:sample_size]

    X_test_sample = X_test[:100]

    model = LogisticRegression(
        max_iter=200,
        random_state=42
    )

    model.fit(
        X_train_sample,
        y_train_sample
    )

    predictions = model.predict(X_test_sample)

    assert len(predictions) == len(X_test_sample)
    assert set(predictions).issubset({0, 1})


def test_processed_data_works_with_random_forest():
    (
        X_train,
        X_test,
        y_train,
        y_test,
        _
    ) = load_processed_data()

    # Keep the sample small because we're testing compatibility,
    # not evaluating Random Forest performance.
    sample_size = 1000

    X_train_sample = X_train[:sample_size]
    y_train_sample = y_train.iloc[:sample_size]

    X_test_sample = X_test[:100]

    model = RandomForestClassifier(
        n_estimators=10,
        random_state=42
    )

    model.fit(
        X_train_sample,
        y_train_sample
    )

    predictions = model.predict(X_test_sample)

    assert len(predictions) == len(X_test_sample)
    assert set(predictions).issubset({0, 1})