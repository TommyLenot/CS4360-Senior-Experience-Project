
import json

import pytest

from src.ingestion.run_replay import (
    load_detection_results,
    run_replay,
)


@pytest.fixture
def sample_results():
    """Synthetic detection results used for testing."""
    return [
        {
            "dataset": "CICIDS2017",
            "record_index": 1,
            "anomaly_score": 0.85,
            "model_prediction": 1,
            "actual_label": 1,
            "attack_type": "DDoS",
        },
        {
            "dataset": "CICIDS2017",
            "record_index": 2,
            "anomaly_score": 0.72,
            "model_prediction": 1,
            "actual_label": 1,
            "attack_type": "PortScan",
        },
        {
            "dataset": "CICIDS2017",
            "record_index": 3,
            "anomaly_score": 0.91,
            "model_prediction": 1,
            "actual_label": 1,
            "attack_type": "DoS Hulk",
        },
    ]


@pytest.fixture
def results_file(tmp_path, sample_results):
    """Create a temporary JSON file for each test."""
    file_path = tmp_path / "detection_results.json"

    file_path.write_text(
        json.dumps(sample_results),
        encoding="utf-8",
    )

    return file_path


def test_load_detection_results(results_file, sample_results):
    results = load_detection_results(results_file)

    assert results == sample_results


def test_load_detection_results_with_utf8_bom(
    tmp_path, sample_results
):
    """PowerShell may create UTF-8 files with a BOM."""
    file_path = tmp_path / "bom_results.json"

    file_path.write_text(
        json.dumps(sample_results),
        encoding="utf-8-sig",
    )

    results = load_detection_results(file_path)

    assert results == sample_results


def test_load_detection_results_missing_file(tmp_path):
    missing_file = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_detection_results(missing_file)


def test_load_detection_results_invalid_json(tmp_path):
    file_path = tmp_path / "invalid.json"
    file_path.write_text(
        "{invalid json",
        encoding="utf-8",
    )

    with pytest.raises(json.JSONDecodeError):
        load_detection_results(file_path)


def test_load_detection_results_not_a_list(tmp_path):
    file_path = tmp_path / "not_a_list.json"

    file_path.write_text(
        json.dumps({"dataset": "CICIDS2017"}),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Detection results must be a JSON list",
    ):
        load_detection_results(file_path)


def test_run_replay_creates_three_alerts(results_file, capsys):
    queue = run_replay(results_file)

    assert queue.size() == 3

    alerts = queue.get_all_alerts()

    assert len(alerts) == 3
    assert [alert.record_index for alert in alerts] == [1, 2, 3]
    assert all(alert.status == "pending" for alert in alerts)
    assert len({alert.alert_id for alert in alerts}) == 3

    output = capsys.readouterr().out

    assert "Starting controlled replay of 3 detection results." in output
    assert "Replay complete. 3 alerts ingested." in output


def test_run_replay_limit(results_file):
    queue = run_replay(results_file, limit=2)

    assert queue.size() == 2

    alerts = queue.get_all_alerts()

    assert [alert.record_index for alert in alerts] == [1, 2]


def test_run_replay_invalid_limit(results_file):
    with pytest.raises(ValueError, match="limit must be at least 1"):
        run_replay(results_file, limit=0)


def test_run_replay_negative_delay(results_file):
    with pytest.raises(
        ValueError,
        match="delay_seconds cannot be negative",
    ):
        run_replay(results_file, delay_seconds=-1)


def test_run_replay_empty_results(tmp_path):
    file_path = tmp_path / "empty_results.json"

    file_path.write_text("[]", encoding="utf-8")

    queue = run_replay(file_path)

    assert queue.size() == 0
