from collections import Counter

from src.data.cicids_loader import (
    get_cicids_files,
    load_cicids_file
)


files = get_cicids_files()

label_counts = Counter()
total_rows = 0

for file_path in files:
    print(f"Checking {file_path.name}...")

    data = load_cicids_file(file_path)

    counts = data["Label"].value_counts()

    for label, count in counts.items():
        label_counts[label] += int(count)

    total_rows += len(data)


print("\nTotal cleaned records:", total_rows)

print("\nOverall label distribution:")

for label, count in label_counts.most_common():
    percentage = (count / total_rows) * 100

    print(
        f"{label}: {count} "
        f"({percentage:.4f}%)"
    )


benign_count = label_counts["BENIGN"]
attack_count = total_rows - benign_count

print("\nBinary distribution:")
print(
    f"BENIGN: {benign_count} "
    f"({(benign_count / total_rows) * 100:.4f}%)"
)
print(
    f"ATTACK: {attack_count} "
    f"({(attack_count / total_rows) * 100:.4f}%)"
)