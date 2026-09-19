from src.ingestion.alert import Alert
from src.ingestion.queue import AlertQueue


class AlertReplay:
    def __init__(self, queue):
        if not isinstance(queue, AlertQueue):
            raise TypeError(
                "queue must be an AlertQueue."
            )

        self.queue = queue

    def create_alert(self, result):
        required_fields = {
            "dataset",
            "record_index",
            "anomaly_score",
            "model_prediction"
        }

        missing_fields = required_fields - result.keys()

        if missing_fields:
            missing = ", ".join(
                sorted(missing_fields)
            )

            raise ValueError(
                f"Detection result is missing required fields: {missing}"
            )

        alert = Alert(
            dataset=result["dataset"],
            record_index=result["record_index"],
            anomaly_score=result["anomaly_score"],
            model_prediction=result["model_prediction"],
            actual_label=result.get("actual_label"),
            attack_type=result.get("attack_type"),
            features=result.get("features", {})
        )

        return alert

    def ingest_result(self, result):
        alert = self.create_alert(result)

        self.queue.add_alert(alert)

        return alert

    def replay(self, results):
        alerts = []

        for result in results:
            alert = self.ingest_result(result)
            alerts.append(alert)

        return alerts