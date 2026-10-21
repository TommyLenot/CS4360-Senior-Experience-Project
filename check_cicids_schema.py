from src.data.cicids_loader import (
    get_cicids_files,
    load_cicids_file
)


files = get_cicids_files()

reference_columns = None
reference_file = None
all_match = True

for file_path in files:
    print(f"Checking {file_path.name}...")

    data = load_cicids_file(file_path)
    columns = list(data.columns)

    if reference_columns is None:
        reference_columns = columns
        reference_file = file_path.name
        continue

    if columns != reference_columns:
        all_match = False

        print(
            f"Schema mismatch between "
            f"{reference_file} and {file_path.name}"
        )

        missing = [
            column
            for column in reference_columns
            if column not in columns
        ]

        extra = [
            column
            for column in columns
            if column not in reference_columns
        ]

        print("Missing columns:", missing)
        print("Extra columns:", extra)


print("\nSchema validation complete.")
print("Files checked:", len(files))
print("Columns per file:", len(reference_columns))
print("All schemas match:", all_match)