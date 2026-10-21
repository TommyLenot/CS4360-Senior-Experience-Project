
import time

from src.ingestion.alert import Alert
from src.ingestion.queue import AlertQueue


class AlertReplay:
    def __init__(self, queue, anomalies_only=False):
        if not isinstance(queue, AlertQueue):
            raise TypeError("queue must be an AlertQueue.")

        self.queue = queue
        self.anomalies_only = anomalies_only

    def create_alert(self, result):
        required_fields = {
            "dataset",
            "record_index",
            "anomaly_score",
            "model_prediction",
        }

        missing_fields = required_fields - result.keys()

        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(
                f"Detection result is missing required fields: {missing}"
            )

        return Alert(
            dataset=result["dataset"],
            record_index=result["record_index"],
            anomaly_score=result["anomaly_score"],
            model_prediction=result["model_prediction"],
            actual_label=result.get("actual_label"),
            attack_type=result.get("attack_type"),
            features=result.get("features", {}),
        )

    def ingest_result(self, result):
        if self.anomalies_only:
            # Validate required fields before deciding whether to skip.
            required_fields = {
                "dataset",
                "record_index",
                "anomaly_score",
                "model_prediction",
            }
            missing_fields = required_fields - result.keys()

            if missing_fields:
                missing = ", ".join(sorted(missing_fields))
                raise ValueError(
                    f"Detection result is missing required fields: {missing}"
                )

            prediction = result["model_prediction"]

            if type(prediction) is not int or prediction not in (0, 1):
                raise ValueError("model_prediction must be 0 or 1.")

            if prediction == 0:
                return None

        alert = self.create_alert(result)
        self.queue.add_alert(alert)

        return alert

    def replay(self, results):
        alerts = []

        for result in results:
            alert = self.ingest_result(result)

            if alert is not None:
                alerts.append(alert)

        return alerts

    def replay_stream(self, results, delay_seconds=0):
        if delay_seconds < 0:
            raise ValueError("delay_seconds cannot be negative.")

        for result in results:
            alert = self.ingest_result(result)

            if alert is not None:
                yield alert

            if delay_seconds > 0:
                time.sleep(delay_seconds)
