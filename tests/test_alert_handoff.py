import pytest

from src.ingestion.alert import Alert
from src.ingestion.handoff import AlertHandoff
from src.ingestion.queue import AlertQueue


def create_alert(record_index=1250):
    return Alert(
        dataset="CICIDS2017",
        record_index=record_index,
        anomaly_score=0.73,
        model_prediction=1,
        actual_label=1,
        attack_type="DDoS",
        features={
            "Destination Port": 80,
            "Flow Duration": 5000
        }
    )


def test_handoff_requires_alert_queue():
    with pytest.raises(TypeError):
        AlertHandoff([])


def test_empty_queue_has_no_pending_alerts():
    queue = AlertQueue()
    handoff = AlertHandoff(queue)

    assert handoff.get_pending_count() == 0
    assert handoff.has_pending_alerts() is False


def test_empty_queue_returns_none():
    queue = AlertQueue()
    handoff = AlertHandoff(queue)

    assert handoff.get_next_pending() is None
    assert handoff.get_next_pending_dict() is None


def test_pending_count():
    queue = AlertQueue()

    queue.add_alert(create_alert(100))
    queue.add_alert(create_alert(200))

    handoff = AlertHandoff(queue)

    assert handoff.get_pending_count() == 2


def test_has_pending_alerts():
    queue = AlertQueue()
    queue.add_alert(create_alert())

    handoff = AlertHandoff(queue)

    assert handoff.has_pending_alerts() is True


def test_get_next_pending_alert():
    queue = AlertQueue()

    first_alert = create_alert(100)
    second_alert = create_alert(200)

    queue.add_alert(first_alert)
    queue.add_alert(second_alert)

    handoff = AlertHandoff(queue)

    result = handoff.get_next_pending()

    assert result.alert_id == first_alert.alert_id
    assert result.record_index == 100
    assert result.status == "pending"


def test_get_next_pending_as_dict():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    handoff = AlertHandoff(queue)

    result = handoff.get_next_pending_dict()

    assert isinstance(result, dict)
    assert result["alert_id"] == alert.alert_id
    assert result["dataset"] == "CICIDS2017"
    assert result["record_index"] == 1250
    assert result["anomaly_score"] == 0.73
    assert result["model_prediction"] == 1
    assert result["actual_label"] == 1
    assert result["attack_type"] == "DDoS"
    assert result["status"] == "pending"


def test_completed_alert_is_not_handed_off():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)
    queue.mark_completed(alert.alert_id)

    handoff = AlertHandoff(queue)

    assert handoff.get_pending_count() == 0
    assert handoff.has_pending_alerts() is False
    assert handoff.get_next_pending() is None


def test_failed_alert_is_not_handed_off():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)
    queue.mark_failed(alert.alert_id)

    handoff = AlertHandoff(queue)

    assert handoff.get_pending_count() == 0
    assert handoff.has_pending_alerts() is False
    assert handoff.get_next_pending() is None


def test_handoff_skips_non_pending_alert():
    queue = AlertQueue()

    completed_alert = create_alert(100)
    pending_alert = create_alert(200)

    queue.add_alert(completed_alert)
    queue.add_alert(pending_alert)

    queue.mark_completed(
        completed_alert.alert_id
    )

    handoff = AlertHandoff(queue)

    result = handoff.get_next_pending()

    assert result.alert_id == pending_alert.alert_id
    assert result.record_index == 200