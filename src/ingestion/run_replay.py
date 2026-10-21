
import argparse
import json
from pathlib import Path

from src.ingestion.queue import AlertQueue
from src.ingestion.replay import AlertReplay


def load_detection_results(input_path):
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Detection results file not found: {path}"
        )

    with path.open("r", encoding="utf-8-sig") as file:
        results = json.load(file)

    if not isinstance(results, list):
        raise ValueError(
            "Detection results must be a JSON list."
        )

    return results


def run_replay(
    input_path,
    delay_seconds=0,
    limit=None,
    anomalies_only=False,
):
    results = load_detection_results(input_path)

    if limit is not None:
        if limit < 1:
            raise ValueError("limit must be at least 1.")

        results = results[:limit]

    queue = AlertQueue()
    replay = AlertReplay(
        queue,
        anomalies_only=anomalies_only,
    )

    print(
        f"Starting controlled replay of "
        f"{len(results)} detection results."
    )

    if anomalies_only:
        print("Anomaly-only filtering enabled.")

    for alert in replay.replay_stream(
        results,
        delay_seconds=delay_seconds,
    ):
        print(
            f"Alert {alert.alert_id} | "
            f"dataset={alert.dataset} | "
            f"record={alert.record_index} | "
            f"prediction={alert.model_prediction} | "
            f"score={alert.anomaly_score} | "
            f"status={alert.status}"
        )

    print(
        f"Replay complete. "
        f"{queue.size()} alerts ingested."
    )

    return queue


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Replay recorded detection results "
            "through the alert ingestion pipeline."
        )
    )

    parser.add_argument(
        "input",
        help="Path to a JSON file containing detection results.",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=0,
        help="Seconds to wait between replayed results. Default: 0.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of results to replay.",
    )

    parser.add_argument(
        "--anomalies-only",
        action="store_true",
        help="Create alerts only for records predicted as anomalous.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    run_replay(
        input_path=args.input,
        delay_seconds=args.delay,
        limit=args.limit,
        anomalies_only=args.anomalies_only,
    )


if __name__ == "__main__":
    main()
