from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


VALID_STATUSES = {
    "pending",
    "completed",
    "failed"
}


@dataclass
class Alert:
    dataset: str
    record_index: int
    anomaly_score: float
    model_prediction: int

    actual_label: int | None = None
    attack_type: str | None = None

    features: dict[str, Any] = field(
        default_factory=dict
    )

    alert_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    timestamp: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    status: str = "pending"

    def __post_init__(self):
        if not self.dataset:
            raise ValueError(
                "dataset cannot be empty."
            )

        if self.record_index < 0:
            raise ValueError(
                "record_index cannot be negative."
            )

        if not isinstance(
            self.anomaly_score,
            (int, float)
        ):
            raise ValueError(
                "anomaly_score must be numeric."
            )

        if self.model_prediction not in {0, 1}:
            raise ValueError(
                "model_prediction must be 0 or 1."
            )

        if (
            self.actual_label is not None
            and self.actual_label not in {0, 1}
        ):
            raise ValueError(
                "actual_label must be 0, 1, or None."
            )

        if self.status not in VALID_STATUSES:
            raise ValueError(
                "status must be pending, completed, or failed."
            )

    def to_dict(self):
        return asdict(self)