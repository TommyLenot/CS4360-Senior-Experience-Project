
import argparse
import json
from pathlib import Path

from src.ingestion.model_adapter import convert_model_outputs


def export_model_results(
    anomaly_scores,
    predictions,
    output_path,
    actual_labels=None,
    dataset="NSL-KDD",
):
    """Export model outputs as ingestion-compatible JSON."""

    results = convert_model_outputs(
        anomaly_scores=anomaly_scores,
        predictions=predictions,
        actual_labels=actual_labels,
        dataset=dataset,
    )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, allow_nan=False)

    return len(results)


def export_from_json(input_path, output_path, dataset="NSL-KDD"):
    """Read arrays of model outputs from JSON and export alert records."""

    with Path(input_path).open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object.")

    return export_model_results(
        anomaly_scores=data["anomaly_scores"],
        predictions=data["predictions"],
        actual_labels=data.get("actual_labels"),
        output_path=output_path,
        dataset=dataset,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Convert model outputs to ingestion-ready JSON."
    )

    parser.add_argument("input", help="Input model-output JSON file")
    parser.add_argument("output", help="Output detection-results JSON file")
    parser.add_argument(
        "--dataset",
        default="NSL-KDD",
        help="Dataset name (default: NSL-KDD)",
    )

    args = parser.parse_args()

    count = export_from_json(
        input_path=args.input,
        output_path=args.output,
        dataset=args.dataset,
    )

    print(f"Exported {count} detection results to {args.output}")


if __name__ == "__main__":
    main()
