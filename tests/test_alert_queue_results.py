import pytest

from src.ingestion.alert import Alert
from src.ingestion.queue import AlertQueue
from src.ingestion.result import InvestigationResult


def create_alert():
    return Alert(
        dataset="CICIDS2017",
        record_index=1250,
        anomaly_score=0.73,
        model_prediction=1,
        actual_label=1,
        attack_type="DDoS",
        features={
            "Destination Port": 80,
            "Flow Duration": 5000
        }
    )


def create_result(alert_id):
    return InvestigationResult(
        alert_id=alert_id,
        verdict="malicious",
        confidence_score=0.85,
        explanation=(
            "The alert contains network behavior "
            "that requires investigation."
        )
    )


def test_add_result():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    result = create_result(alert.alert_id)
    returned_result = queue.add_result(result)

    assert returned_result is result


def test_result_can_be_retrieved():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    result = create_result(alert.alert_id)
    queue.add_result(result)

    stored_result = queue.get_result(
        alert.alert_id
    )

    assert stored_result.alert_id == alert.alert_id
    assert stored_result.verdict == "malicious"
    assert stored_result.confidence_score == 0.85


def test_add_result_marks_alert_completed():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    assert alert.status == "pending"

    result = create_result(alert.alert_id)
    queue.add_result(result)

    assert alert.status == "completed"


def test_completed_alert_not_pending():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    result = create_result(alert.alert_id)
    queue.add_result(result)

    assert alert not in queue.get_pending_alerts()


def test_has_result_false_before_result():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    assert queue.has_result(
        alert.alert_id
    ) is False


def test_has_result_true_after_result():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    result = create_result(alert.alert_id)
    queue.add_result(result)

    assert queue.has_result(
        alert.alert_id
    ) is True


def test_result_for_missing_alert_rejected():
    queue = AlertQueue()

    result = create_result(
        "missing-alert"
    )

    with pytest.raises(KeyError):
        queue.add_result(result)


def test_duplicate_result_rejected():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    first_result = create_result(
        alert.alert_id
    )

    second_result = create_result(
        alert.alert_id
    )

    queue.add_result(first_result)

    with pytest.raises(ValueError):
        queue.add_result(second_result)


def test_invalid_result_object_rejected():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    with pytest.raises(TypeError):
        queue.add_result(
            {
                "alert_id": alert.alert_id,
                "verdict": "malicious"
            }
        )


def test_missing_result_rejected():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    with pytest.raises(KeyError):
        queue.get_result(
            alert.alert_id
        )


def test_result_preserves_explanation():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    result = create_result(alert.alert_id)
    queue.add_result(result)

    stored_result = queue.get_result(
        alert.alert_id
    )

    assert stored_result.explanation == (
        "The alert contains network behavior "
        "that requires investigation."
    )


def test_result_preserves_completion_time():
    queue = AlertQueue()
    alert = create_alert()

    queue.add_alert(alert)

    result = create_result(alert.alert_id)
    queue.add_result(result)

    stored_result = queue.get_result(
        alert.alert_id
    )

    assert stored_result.completed_at