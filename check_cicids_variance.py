from src.data.cicids_loader import (
    get_cicids_files,
    load_cicids_file
)


files = get_cicids_files()

all_features = None
varying_features = set()

for file_path in files:
    print(f"Checking {file_path.name}...")

    data = load_cicids_file(file_path)
    X = data.drop(columns=["Label"])

    if all_features is None:
        all_features = set(X.columns)

    for column in X.columns:
        if X[column].nunique(dropna=False) > 1:
            varying_features.add(column)

constant_features = sorted(
    all_features - varying_features
)

print("\nTotal features:", len(all_features))
print("Features that vary:", len(varying_features))
print(
    "Constant across all files:",
    len(constant_features)
)
print(constant_features)