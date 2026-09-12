import pandas as pd

from sklearn.ensemble import IsolationForest

from src.data.preprocessing import preprocess_train_test


def test_preprocessed_data_works_with_isolation_forest():
    train_data = pd.DataFrame({
        "protocol_type": ["tcp", "udp", "tcp", "icmp"],
        "service": ["http", "domain_u", "ftp", "eco_i"],
        "flag": ["SF", "SF", "REJ", "SF"],
        "duration": [0, 5, 10, 2],
        "src_bytes": [100, 200, 300, 50],
        "label": ["normal", "neptune", "normal", "smurf"],
        "difficulty": [20, 15, 18, 17]
    })

    test_data = pd.DataFrame({
        "protocol_type": ["tcp", "udp"],
        "service": ["http", "domain_u"],
        "flag": ["SF", "SF"],
        "duration": [1, 7],
        "src_bytes": [120, 220],
        "label": ["normal", "neptune"],
        "difficulty": [19, 16]
    })

    (
        X_train_processed,
        X_test_processed,
        y_train,
        y_test,
        preprocessor
    ) = preprocess_train_test(train_data, test_data)

    model = IsolationForest(
        random_state=42,
        contamination="auto"
    )

    model.fit(X_train_processed)

    predictions = model.predict(X_test_processed)

    assert len(predictions) == 2