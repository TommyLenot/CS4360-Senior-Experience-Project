from src.data.loader import load_nsl_kdd
from src.data.preprocessing import (
    preprocess_train_test,
    save_processed_data
)


TRAIN_PATH = "data/raw/KDDTrain+.txt"
TEST_PATH = "data/raw/KDDTest+.txt"


def main():
    print("Loading NSL-KDD data...")

    train_data = load_nsl_kdd(TRAIN_PATH)
    test_data = load_nsl_kdd(TEST_PATH)

    print("Training shape:", train_data.shape)
    print("Test shape:", test_data.shape)

    print("\nPreprocessing data...")

    (
        X_train_processed,
        X_test_processed,
        y_train,
        y_test,
        preprocessor
    ) = preprocess_train_test(train_data, test_data)

    print("Processed training shape:", X_train_processed.shape)
    print("Processed test shape:", X_test_processed.shape)

    print("\nSaving processed data...")

    save_processed_data(
        X_train_processed,
        X_test_processed,
        y_train,
        y_test,
        preprocessor
    )

    print("Processed data saved successfully to data/processed/")


if __name__ == "__main__":
    main()