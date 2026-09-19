import pytest

from src.ingestion.queue import AlertQueue
from src.ingestion.replay import AlertReplay


def create_detection_result(record_index=0):
    return {
        "dataset": "CICIDS2017",
        "record_index": record_index,
        "anomaly_score": 0.73,
        "model_prediction": 1,
        "actual_label": 1,
        "attack_type": "DDoS",
        "features": {
            "Destination Port": 80,
            "Flow Duration": 5000
        }
    }


def test_invalid_queue_rejected():
    with pytest.raises(
        TypeError,
        match="queue must be an AlertQueue"
    ):
        AlertReplay([])


def test_create_alert():
    queue = AlertQueue()
    replay = AlertReplay(queue)

    result = create_detection_result()

    alert = replay.create_alert(result)

    assert alert.dataset == "CICIDS2017"
    assert alert.record_index == 0
    assert alert.anomaly_score == 0.73
    assert alert.model_prediction == 1
    assert alert.actual_label == 1
    assert alert.attack_type == "DDoS"
    assert alert.status == "pending"

    assert alert.features == {
        "Destination Port": 80,
        "Flow Duration": 5000
    }


def test_create_alert_does_not_add_to_queue():
    queue = AlertQueue()
    replay = AlertReplay(queue)

    result = create_detection_result()

    replay.create_alert(result)

    assert queue.is_empty()


def test_ingest_result_adds_alert_to_queue():
    queue = AlertQueue()
    replay = AlertReplay(queue)

    result = create_detection_result()

    alert = replay.ingest_result(result)

    assert queue.size() == 1
    assert queue.get_alert(
        alert.alert_id
    ) is alert


def test_replay_multiple_results():
    queue = AlertQueue()
    replay = AlertReplay(queue)

    results = [
        create_detection_result(1),
        create_detection_result(2),
        create_detection_result(3)
    ]

    alerts = replay.replay(results)

    assert len(alerts) == 3
    assert queue.size() == 3

    assert [
        alert.record_index
        for alert in alerts
    ] == [1, 2, 3]


def test_replay_alerts_start_pending():
    queue = AlertQueue()
    replay = AlertReplay(queue)

    results = [
        create_detection_result(1),
        create_detection_result(2)
    ]

    replay.replay(results)

    pending_alerts = queue.get_pending_alerts()

    assert len(pending_alerts) == 2


def test_optional_fields_can_be_omitted():
    queue = AlertQueue()
    replay = AlertReplay(queue)

    result = {
        "dataset": "CICIDS2017",
        "record_index": 10,
        "anomaly_score": 0.65,
        "model_prediction": 1
    }

    alert = replay.ingest_result(result)

    assert alert.actual_label is None
    assert alert.attack_type is None
    assert alert.features == {}


@pytest.mark.parametrize(
    "missing_field",
    [
        "dataset",
        "record_index",
        "anomaly_score",
        "model_prediction"
    ]
)
def test_missing_required_field_rejected(
    missing_field
):
    queue = AlertQueue()
    replay = AlertReplay(queue)

    result = create_detection_result()

    del result[missing_field]

    with pytest.raises(
        ValueError,
        match="missing required fields"
    ):
        replay.ingest_result(result)

    assert queue.is_empty()