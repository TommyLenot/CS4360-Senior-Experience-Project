
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
            "Flow Duration": 5000,
        },
    }


def test_invalid_queue_rejected():
    with pytest.raises(
        TypeError,
        match="queue must be an AlertQueue",
    ):
        AlertReplay([])


def test_create_alert():
    queue = AlertQueue()
    replay = AlertReplay(queue)
    alert = replay.create_alert(create_detection_result())

    assert alert.dataset == "CICIDS2017"
    assert alert.record_index == 0
    assert alert.anomaly_score == 0.73
    assert alert.model_prediction == 1
    assert alert.actual_label == 1
    assert alert.attack_type == "DDoS"
    assert alert.status == "pending"
    assert alert.features == {
        "Destination Port": 80,
        "Flow Duration": 5000,
    }


def test_create_alert_does_not_add_to_queue():
    queue = AlertQueue()
    replay = AlertReplay(queue)

    replay.create_alert(create_detection_result())

    assert queue.is_empty()


def test_ingest_result_adds_alert_to_queue():
    queue = AlertQueue()
    replay = AlertReplay(queue)

    alert = replay.ingest_result(create_detection_result())

    assert queue.size() == 1
    assert queue.get_alert(alert.alert_id) is alert


def test_replay_multiple_results():
    queue = AlertQueue()
    replay = AlertReplay(queue)
    results = [
        create_detection_result(1),
        create_detection_result(2),
        create_detection_result(3),
    ]

    alerts = replay.replay(results)

    assert len(alerts) == 3
    assert queue.size() == 3
    assert [alert.record_index for alert in alerts] == [1, 2, 3]


def test_replay_alerts_start_pending():
    queue = AlertQueue()
    replay = AlertReplay(queue)

    replay.replay([
        create_detection_result(1),
        create_detection_result(2),
    ])

    assert len(queue.get_pending_alerts()) == 2


def test_optional_fields_can_be_omitted():
    queue = AlertQueue()
    replay = AlertReplay(queue)
    result = {
        "dataset": "CICIDS2017",
        "record_index": 10,
        "anomaly_score": 0.65,
        "model_prediction": 1,
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
        "model_prediction",
    ],
)
def test_missing_required_field_rejected(missing_field):
    queue = AlertQueue()
    replay = AlertReplay(queue)
    result = create_detection_result()
    del result[missing_field]

    with pytest.raises(ValueError, match="missing required fields"):
        replay.ingest_result(result)

    assert queue.is_empty()


def test_replay_stream_processes_results_in_order():
    queue = AlertQueue()
    replay = AlertReplay(queue)
    results = [
        create_detection_result(1),
        create_detection_result(2),
        create_detection_result(3),
    ]

    alerts = list(replay.replay_stream(results, delay_seconds=0))

    assert queue.size() == 3
    assert [alert.record_index for alert in alerts] == [1, 2, 3]


def test_replay_stream_adds_alerts_incrementally():
    queue = AlertQueue()
    replay = AlertReplay(queue)
    stream = replay.replay_stream([
        create_detection_result(1),
        create_detection_result(2),
    ])

    assert queue.size() == 0

    first_alert = next(stream)
    assert first_alert.record_index == 1
    assert queue.size() == 1

    second_alert = next(stream)
    assert second_alert.record_index == 2
    assert queue.size() == 2

    with pytest.raises(StopIteration):
        next(stream)


def test_replay_stream_alerts_start_pending():
    queue = AlertQueue()
    replay = AlertReplay(queue)

    list(replay.replay_stream([
        create_detection_result(1),
        create_detection_result(2),
    ]))

    assert len(queue.get_pending_alerts()) == 2


def test_replay_stream_rejects_negative_delay():
    queue = AlertQueue()
    replay = AlertReplay(queue)
    stream = replay.replay_stream(
        [create_detection_result(1)],
        delay_seconds=-1,
    )

    with pytest.raises(
        ValueError,
        match="delay_seconds cannot be negative",
    ):
        next(stream)

    assert queue.is_empty()


# New tests for anomaly-only filtering

def test_anomalies_only_skips_normal_traffic():
    queue = AlertQueue()
    replay = AlertReplay(queue, anomalies_only=True)
    normal = create_detection_result(1)
    normal["model_prediction"] = 0

    assert replay.ingest_result(normal) is None
    assert queue.is_empty()


def test_anomalies_only_keeps_anomalous_traffic():
    queue = AlertQueue()
    replay = AlertReplay(queue, anomalies_only=True)

    alert = replay.ingest_result(create_detection_result(2))

    assert alert is not None
    assert alert.record_index == 2
    assert queue.size() == 1


def test_anomalies_only_filters_mixed_results():
    queue = AlertQueue()
    replay = AlertReplay(queue, anomalies_only=True)
    results = [create_detection_result(i) for i in range(5)]
    results[1]["model_prediction"] = 0
    results[3]["model_prediction"] = 0

    alerts = replay.replay(results)

    assert len(alerts) == 3
    assert queue.size() == 3
    assert [alert.record_index for alert in alerts] == [0, 2, 4]


def test_anomalies_only_filters_stream():
    queue = AlertQueue()
    replay = AlertReplay(queue, anomalies_only=True)
    results = [create_detection_result(i) for i in range(4)]
    results[0]["model_prediction"] = 0
    results[2]["model_prediction"] = 0

    alerts = list(replay.replay_stream(results))

    assert len(alerts) == 2
    assert [alert.record_index for alert in alerts] == [1, 3]
    assert queue.size() == 2


def test_default_mode_still_accepts_normal_traffic():
    queue = AlertQueue()
    replay = AlertReplay(queue)
    normal = create_detection_result(5)
    normal["model_prediction"] = 0

    alert = replay.ingest_result(normal)

    assert alert is not None
    assert queue.size() == 1
