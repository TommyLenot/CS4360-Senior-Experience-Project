
import json

import pytest

from src.ingestion.export_results import (
    export_model_results,
    export_from_json,
)
from src.ingestion.run_replay import load_detection_results
from src.ingestion.queue import AlertQueue
from src.ingestion.replay import AlertReplay


def test_export_model_results(tmp_path):
    output = tmp_path / "detection_results.json"

    count = export_model_results(
        anomaly_scores=[125.4, 32.1, 210.7],
        predictions=[1, 0, 1],
        actual_labels=[1, 0, 1],
        output_path=output,
    )

    assert count == 3
    assert output.exists()

    with output.open("r", encoding="utf-8") as file:
        results = json.load(file)

    assert len(results) == 3
    assert results[0]["dataset"] == "NSL-KDD"
    assert results[0]["anomaly_score"] == 125.4
    assert results[1]["model_prediction"] == 0
    assert results[2]["actual_label"] == 1


def test_export_without_labels(tmp_path):
    output = tmp_path / "results.json"

    export_model_results(
        anomaly_scores=[15.5],
        predictions=[1],
        output_path=output,
    )

    results = load_detection_results(output)

    assert len(results) == 1
    assert "actual_label" not in results[0]


def test_export_custom_dataset(tmp_path):
    output = tmp_path / "results.json"

    export_model_results(
        anomaly_scores=[50.0],
        predictions=[1],
        output_path=output,
        dataset="CICIDS2017",
    )

    results = load_detection_results(output)

    assert results[0]["dataset"] == "CICIDS2017"


def test_export_creates_output_directory(tmp_path):
    output = tmp_path / "nested" / "folder" / "results.json"

    export_model_results(
        anomaly_scores=[25.0],
        predictions=[1],
        output_path=output,
    )

    assert output.exists()


def test_export_from_json(tmp_path):
    input_file = tmp_path / "model_outputs.json"
    output_file = tmp_path / "detection_results.json"

    input_data = {
        "anomaly_scores": [125.4, 32.1],
        "predictions": [1, 0],
        "actual_labels": [1, 0],
    }

    input_file.write_text(
        json.dumps(input_data),
        encoding="utf-8",
    )

    count = export_from_json(input_file, output_file)

    results = load_detection_results(output_file)

    assert count == 2
    assert len(results) == 2
    assert results[0]["model_prediction"] == 1
    assert results[1]["model_prediction"] == 0


def test_export_rejects_invalid_input(tmp_path):
    input_file = tmp_path / "invalid.json"
    output_file = tmp_path / "results.json"

    input_file.write_text(
        json.dumps([1, 2, 3]),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        export_from_json(input_file, output_file)


def test_export_rejects_mismatched_arrays(tmp_path):
    output = tmp_path / "results.json"

    with pytest.raises(ValueError):
        export_model_results(
            anomaly_scores=[10.0, 20.0],
            predictions=[1],
            output_path=output,
        )


def test_export_integrates_with_ingestion(tmp_path):
    output = tmp_path / "results.json"

    export_model_results(
        anomaly_scores=[125.4, 32.1, 210.7],
        predictions=[1, 0, 1],
        actual_labels=[1, 0, 1],
        output_path=output,
    )

    results = load_detection_results(output)

    queue = AlertQueue()
    replay = AlertReplay(queue)

    alerts = replay.replay(results)

    assert len(alerts) == 3
    assert queue.size() == 3

    assert alerts[0].dataset == "NSL-KDD"
    assert alerts[0].anomaly_score == 125.4
    assert alerts[1].model_prediction == 0
    assert alerts[2].record_index == 2
