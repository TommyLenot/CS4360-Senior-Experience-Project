import pytest

from src.ingestion.result import InvestigationResult


def create_valid_result():
    return InvestigationResult(
        alert_id="test-alert-1",
        verdict="malicious",
        confidence_score=0.85,
        explanation=(
            "The alert contains network behavior "
            "that requires investigation."
        )
    )


def test_create_valid_result():
    result = create_valid_result()

    assert result.alert_id == "test-alert-1"
    assert result.verdict == "malicious"
    assert result.confidence_score == 0.85
    assert result.explanation
    assert result.completed_at


def test_result_to_dict():
    result = create_valid_result()

    result_dict = result.to_dict()

    assert isinstance(result_dict, dict)
    assert result_dict["alert_id"] == "test-alert-1"
    assert result_dict["verdict"] == "malicious"
    assert result_dict["confidence_score"] == 0.85
    assert result_dict["explanation"]
    assert result_dict["completed_at"]


def test_empty_alert_id_rejected():
    with pytest.raises(ValueError):
        InvestigationResult(
            alert_id="",
            verdict="malicious",
            confidence_score=0.85,
            explanation="Test explanation."
        )


@pytest.mark.parametrize(
    "verdict",
    [
        "benign",
        "suspicious",
        "malicious",
        "inconclusive"
    ]
)
def test_valid_verdicts(verdict):
    result = InvestigationResult(
        alert_id="test-alert-1",
        verdict=verdict,
        confidence_score=0.85,
        explanation="Test explanation."
    )

    assert result.verdict == verdict


def test_invalid_verdict_rejected():
    with pytest.raises(ValueError):
        InvestigationResult(
            alert_id="test-alert-1",
            verdict="unknown",
            confidence_score=0.85,
            explanation="Test explanation."
        )


def test_non_numeric_confidence_rejected():
    with pytest.raises(ValueError):
        InvestigationResult(
            alert_id="test-alert-1",
            verdict="malicious",
            confidence_score="high",
            explanation="Test explanation."
        )


@pytest.mark.parametrize(
    "confidence_score",
    [
        -0.01,
        1.01
    ]
)
def test_confidence_outside_range_rejected(
    confidence_score
):
    with pytest.raises(ValueError):
        InvestigationResult(
            alert_id="test-alert-1",
            verdict="malicious",
            confidence_score=confidence_score,
            explanation="Test explanation."
        )


@pytest.mark.parametrize(
    "confidence_score",
    [
        0.0,
        1.0
    ]
)
def test_confidence_boundaries_allowed(
    confidence_score
):
    result = InvestigationResult(
        alert_id="test-alert-1",
        verdict="malicious",
        confidence_score=confidence_score,
        explanation="Test explanation."
    )

    assert result.confidence_score == confidence_score


def test_empty_explanation_rejected():
    with pytest.raises(ValueError):
        InvestigationResult(
            alert_id="test-alert-1",
            verdict="malicious",
            confidence_score=0.85,
            explanation=""
        )


def test_whitespace_explanation_rejected():
    with pytest.raises(ValueError):
        InvestigationResult(
            alert_id="test-alert-1",
            verdict="malicious",
            confidence_score=0.85,
            explanation="   "
        )


def test_custom_completed_at_preserved():
    timestamp = "2026-09-19T00:00:00+00:00"

    result = InvestigationResult(
        alert_id="test-alert-1",
        verdict="benign",
        confidence_score=0.90,
        explanation="Test explanation.",
        completed_at=timestamp
    )

    assert result.completed_at == timestamp