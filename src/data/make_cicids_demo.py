"""Build artifacts/cicids2017/demo.csv.gz, the rows the dashboard replays.

It uses the same per-file 80/20 split as prepare_cicids_data.py (same seed), so the
demo rows come from the held-out test part, then takes a stratified sample so the
dashboard stays quick. Run it once from the project root:

    python -m src.data.make_cicids_demo
"""
import gc
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from src.data.cicids_loader import DEFAULT_CICIDS_DIR, get_cicids_files, load_cicids_file
from src.data.prepare_cicids_data import RANDOM_STATE, split_file_data

DEMO_ROWS = 25_000
DEMO_PATH = Path("artifacts/cicids2017/demo.csv.gz")


def build_demo(data_dir=DEFAULT_CICIDS_DIR, out_path=DEMO_PATH, n_rows=DEMO_ROWS):
    test_parts = []
    for file_path in get_cicids_files(data_dir):
        print(f"Processing {file_path.name}...")
        data = load_cicids_file(file_path)
        data["source_file"] = file_path.name
        _, test_part = split_file_data(data)  # keep only the held-out part
        test_parts.append(test_part)
        del data
        gc.collect()

    test = pd.concat(test_parts, ignore_index=True)
    del test_parts
    gc.collect()

    if n_rows < len(test):
        demo, _ = train_test_split(
            test, train_size=n_rows, stratify=test["Label"], random_state=RANDOM_STATE
        )
    else:
        demo = test
    demo = demo.reset_index(drop=True)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    demo.to_csv(out_path, index=False, compression="gzip")
    print(f"Saved {len(demo):,} rows to {out_path}")
    print(demo["Label"].value_counts())
    return demo


if __name__ == "__main__":
    build_demo()