from dataclasses import asdict, dataclass
from datetime import datetime, timezone


VALID_VERDICTS = {
    "benign",
    "suspicious",
    "malicious",
    "inconclusive"
}


@dataclass
class InvestigationResult:
    alert_id: str
    verdict: str
    confidence_score: float
    explanation: str

    completed_at: str = ""

    def __post_init__(self):
        if not self.alert_id:
            raise ValueError(
                "alert_id cannot be empty."
            )

        if self.verdict not in VALID_VERDICTS:
            raise ValueError(
                "verdict must be benign, suspicious, "
                "malicious, or inconclusive."
            )

        if not isinstance(
            self.confidence_score,
            (int, float)
        ):
            raise ValueError(
                "confidence_score must be numeric."
            )

        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError(
                "confidence_score must be between 0 and 1."
            )

        if not self.explanation.strip():
            raise ValueError(
                "explanation cannot be empty."
            )

        if not self.completed_at:
            self.completed_at = datetime.now(
                timezone.utc
            ).isoformat()

    def to_dict(self):
        return asdict(self)