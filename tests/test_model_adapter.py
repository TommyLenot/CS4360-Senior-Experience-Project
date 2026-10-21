
import pytest

from src.ingestion.model_adapter import convert_model_outputs
from src.ingestion.queue import AlertQueue
from src.ingestion.replay import AlertReplay


def test_convert_model_outputs():
    results = convert_model_outputs(
        anomaly_scores=[125.4, 32.1, 210.7],
        predictions=[1, 0, 1],
        actual_labels=[1, 0, 1],
    )

    assert len(results) == 3

    assert results[0] == {
        "dataset": "NSL-KDD",
        "record_index": 0,
        "anomaly_score": 125.4,
        "model_prediction": 1,
        "actual_label": 1,
    }

    assert results[1]["model_prediction"] == 0
    assert results[2]["record_index"] == 2


def test_convert_without_actual_labels():
    results = convert_model_outputs(
        anomaly_scores=[10.5],
        predictions=[1],
    )

    assert len(results) == 1
    assert "actual_label" not in results[0]


def test_custom_dataset_name():
    results = convert_model_outputs(
        anomaly_scores=[50.0],
        predictions=[1],
        dataset="CICIDS2017",
    )

    assert results[0]["dataset"] == "CICIDS2017"


def test_mismatched_scores_and_predictions():
    with pytest.raises(ValueError):
        convert_model_outputs(
            anomaly_scores=[10.0, 20.0],
            predictions=[1],
        )


def test_mismatched_actual_labels():
    with pytest.raises(ValueError):
        convert_model_outputs(
            anomaly_scores=[10.0, 20.0],
            predictions=[1, 0],
            actual_labels=[1],
        )


@pytest.mark.parametrize(
    "invalid_score",
    [float("nan"), float("inf"), float("-inf")],
)
def test_invalid_anomaly_scores(invalid_score):
    with pytest.raises(ValueError):
        convert_model_outputs(
            anomaly_scores=[invalid_score],
            predictions=[1],
        )


def test_invalid_prediction():
    with pytest.raises(ValueError):
        convert_model_outputs(
            anomaly_scores=[10.0],
            predictions=[2],
        )


def test_invalid_actual_label():
    with pytest.raises(ValueError):
        convert_model_outputs(
            anomaly_scores=[10.0],
            predictions=[1],
            actual_labels=[3],
        )


def test_adapter_integrates_with_alert_queue():
    results = convert_model_outputs(
        anomaly_scores=[125.4, 32.1, 210.7],
        predictions=[1, 0, 1],
        actual_labels=[1, 0, 1],
    )

    queue = AlertQueue()
    replay = AlertReplay(queue)

    alerts = replay.replay(results)

    assert len(alerts) == 3
    assert queue.size() == 3

    assert alerts[0].dataset == "NSL-KDD"
    assert alerts[0].anomaly_score == 125.4
    assert alerts[0].model_prediction == 1
    assert alerts[0].actual_label == 1

    assert alerts[1].model_prediction == 0
    assert alerts[2].record_index == 2
