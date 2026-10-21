import pytest

from src.ingestion.alert import Alert


def create_valid_alert():
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


def test_create_valid_alert():
    alert = create_valid_alert()

    assert alert.dataset == "CICIDS2017"
    assert alert.record_index == 1250
    assert alert.anomaly_score == 0.73
    assert alert.model_prediction == 1
    assert alert.actual_label == 1
    assert alert.attack_type == "DDoS"
    assert alert.status == "pending"

    assert alert.alert_id
    assert alert.timestamp

    assert alert.features == {
        "Destination Port": 80,
        "Flow Duration": 5000
    }


def test_alert_to_dict():
    alert = create_valid_alert()

    result = alert.to_dict()

    assert result["dataset"] == "CICIDS2017"
    assert result["record_index"] == 1250
    assert result["anomaly_score"] == 0.73
    assert result["model_prediction"] == 1
    assert result["actual_label"] == 1
    assert result["attack_type"] == "DDoS"
    assert result["status"] == "pending"

    assert "alert_id" in result
    assert "timestamp" in result
    assert "features" in result


def test_empty_dataset_rejected():
    with pytest.raises(
        ValueError,
        match="dataset cannot be empty"
    ):
        Alert(
            dataset="",
            record_index=0,
            anomaly_score=0.5,
            model_prediction=1
        )


def test_negative_record_index_rejected():
    with pytest.raises(
        ValueError,
        match="record_index cannot be negative"
    ):
        Alert(
            dataset="CICIDS2017",
            record_index=-1,
            anomaly_score=0.5,
            model_prediction=1
        )


def test_non_numeric_anomaly_score_rejected():
    with pytest.raises(
        ValueError,
        match="anomaly_score must be numeric"
    ):
        Alert(
            dataset="CICIDS2017",
            record_index=0,
            anomaly_score="high",
            model_prediction=1
        )


def test_invalid_model_prediction_rejected():
    with pytest.raises(
        ValueError,
        match="model_prediction must be 0 or 1"
    ):
        Alert(
            dataset="CICIDS2017",
            record_index=0,
            anomaly_score=0.5,
            model_prediction=2
        )


def test_invalid_actual_label_rejected():
    with pytest.raises(
        ValueError,
        match="actual_label must be 0, 1, or None"
    ):
        Alert(
            dataset="CICIDS2017",
            record_index=0,
            anomaly_score=0.5,
            model_prediction=1,
            actual_label=2
        )


def test_invalid_status_rejected():
    with pytest.raises(
        ValueError,
        match="status must be pending, completed, or failed"
    ):
        Alert(
            dataset="CICIDS2017",
            record_index=0,
            anomaly_score=0.5,
            model_prediction=1,
            status="unknown"
        )


def test_optional_ground_truth():
    alert = Alert(
        dataset="CICIDS2017",
        record_index=100,
        anomaly_score=0.42,
        model_prediction=1
    )

    assert alert.actual_label is None
    assert alert.attack_type is None
    assert alert.status == "pending"