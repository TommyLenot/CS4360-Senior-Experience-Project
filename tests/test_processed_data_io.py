import pandas as pd

from src.data.preprocessing import (
    preprocess_train_test,
    save_processed_data,
    load_processed_data
)


def test_save_and_load_processed_data(tmp_path):
    train_data = pd.DataFrame({
        "protocol_type": ["tcp", "udp", "tcp"],
        "service": ["http", "domain_u", "ftp"],
        "flag": ["SF", "SF", "REJ"],
        "duration": [0, 2, 5],
        "src_bytes": [100, 200, 300],
        "label": ["normal", "neptune", "normal"],
        "difficulty": [1, 2, 3]
    })

    test_data = pd.DataFrame({
        "protocol_type": ["tcp", "icmp"],
        "service": ["http", "eco_i"],
        "flag": ["SF", "SF"],
        "duration": [1, 4],
        "src_bytes": [150, 250],
        "label": ["normal", "smurf"],
        "difficulty": [1, 2]
    })

    (
        X_train_processed,
        X_test_processed,
        y_train,
        y_test,
        preprocessor
    ) = preprocess_train_test(train_data, test_data)

    save_processed_data(
        X_train_processed,
        X_test_processed,
        y_train,
        y_test,
        preprocessor,
        output_dir=tmp_path
    )

    (
        loaded_X_train,
        loaded_X_test,
        loaded_y_train,
        loaded_y_test,
        loaded_preprocessor
    ) = load_processed_data(output_dir=tmp_path)

    assert loaded_X_train.shape == X_train_processed.shape
    assert loaded_X_test.shape == X_test_processed.shape
    assert loaded_y_train.equals(y_train)
    assert loaded_y_test.equals(y_test)
    assert loaded_preprocessor is not None