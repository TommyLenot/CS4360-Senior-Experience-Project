import pytest

from src.ingestion.alert import Alert
from src.ingestion.queue import AlertQueue


def create_alert(record_index=0):
    return Alert(
        dataset="CICIDS2017",
        record_index=record_index,
        anomaly_score=0.75,
        model_prediction=1,
        actual_label=1,
        attack_type="DDoS",
        features={
            "Destination Port": 80,
            "Flow Duration": 5000
        }
    )


def test_new_queue_is_empty():
    queue = AlertQueue()

    assert queue.is_empty()
    assert queue.size() == 0


def test_add_alert():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    assert queue.size() == 1
    assert not queue.is_empty()


def test_get_alert():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    result = queue.get_alert(alert.alert_id)

    assert result is alert


def test_get_all_alerts():
    queue = AlertQueue()

    first_alert = create_alert(1)
    second_alert = create_alert(2)

    queue.add_alert(first_alert)
    queue.add_alert(second_alert)

    alerts = queue.get_all_alerts()

    assert len(alerts) == 2
    assert first_alert in alerts
    assert second_alert in alerts


def test_get_pending_alerts():
    queue = AlertQueue()

    first_alert = create_alert(1)
    second_alert = create_alert(2)

    queue.add_alert(first_alert)
    queue.add_alert(second_alert)

    queue.mark_completed(first_alert.alert_id)

    pending_alerts = queue.get_pending_alerts()

    assert len(pending_alerts) == 1
    assert second_alert in pending_alerts
    assert first_alert not in pending_alerts


def test_mark_alert_completed():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    result = queue.mark_completed(
        alert.alert_id
    )

    assert result.status == "completed"
    assert alert.status == "completed"


def test_mark_alert_failed():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    result = queue.mark_failed(
        alert.alert_id
    )

    assert result.status == "failed"
    assert alert.status == "failed"


def test_duplicate_alert_rejected():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    with pytest.raises(
        ValueError,
        match="already exists"
    ):
        queue.add_alert(alert)


def test_invalid_object_rejected():
    queue = AlertQueue()

    with pytest.raises(
        TypeError,
        match="Only Alert objects"
    ):
        queue.add_alert(
            {
                "dataset": "CICIDS2017"
            }
        )


def test_missing_alert_rejected():
    queue = AlertQueue()

    with pytest.raises(
        KeyError,
        match="was not found"
    ):
        queue.get_alert(
            "missing-alert-id"
        )