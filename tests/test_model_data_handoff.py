import numpy as np

from src.data.preprocessing import load_processed_data


def test_saved_model_data_handoff():
    (
        X_train,
        X_test,
        y_train,
        y_test,
        preprocessor
    ) = load_processed_data()

    # Feature matrices and labels must have matching row counts.
    assert X_train.shape[0] == len(y_train)
    assert X_test.shape[0] == len(y_test)

    # Training and test data must use the same feature space.
    assert X_train.shape[1] == X_test.shape[1]

    # Week 3 models need numeric feature matrices.
    assert np.issubdtype(X_train.dtype, np.number)
    assert np.issubdtype(X_test.dtype, np.number)

    # Model input must not contain NaN or infinite values.
    assert np.isfinite(X_train).all()
    assert np.isfinite(X_test).all()

    # Labels must follow the project's binary convention:
    # 0 = normal, 1 = attack.
    assert set(y_train.unique()).issubset({0, 1})
    assert set(y_test.unique()).issubset({0, 1})

    # Both classes should exist in the saved datasets.
    assert set(y_train.unique()) == {0, 1}
    assert set(y_test.unique()) == {0, 1}

    # The fitted preprocessor must also be available for reuse.
    assert preprocessor is not None