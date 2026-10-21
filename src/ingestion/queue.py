from src.ingestion.alert import Alert
from src.ingestion.result import InvestigationResult


class AlertQueue:
    def __init__(self):
        self._alerts = {}
        self._results = {}

    def add_alert(self, alert):
        if not isinstance(alert, Alert):
            raise TypeError(
                "Only Alert objects can be added to the queue."
            )

        if alert.alert_id in self._alerts:
            raise ValueError(
                f"Alert {alert.alert_id} already exists."
            )

        self._alerts[alert.alert_id] = alert

    def get_alert(self, alert_id):
        if alert_id not in self._alerts:
            raise KeyError(
                f"Alert {alert_id} was not found."
            )

        return self._alerts[alert_id]

    def get_all_alerts(self):
        return list(self._alerts.values())

    def get_pending_alerts(self):
        return [
            alert
            for alert in self._alerts.values()
            if alert.status == "pending"
        ]

    def add_result(self, result):
        if not isinstance(
            result,
            InvestigationResult
        ):
            raise TypeError(
                "Only InvestigationResult objects "
                "can be added."
            )

        if result.alert_id not in self._alerts:
            raise KeyError(
                f"Alert {result.alert_id} was not found."
            )

        if result.alert_id in self._results:
            raise ValueError(
                f"Alert {result.alert_id} already "
                "has an investigation result."
            )

        self._results[result.alert_id] = result

        alert = self._alerts[result.alert_id]
        alert.status = "completed"

        return result

    def get_result(self, alert_id):
        if alert_id not in self._results:
            raise KeyError(
                f"No investigation result found "
                f"for alert {alert_id}."
            )

        return self._results[alert_id]

    def has_result(self, alert_id):
        return alert_id in self._results

    def mark_completed(self, alert_id):
        alert = self.get_alert(alert_id)
        alert.status = "completed"

        return alert

    def mark_failed(self, alert_id):
        alert = self.get_alert(alert_id)
        alert.status = "failed"

        return alert

    def size(self):
        return len(self._alerts)

    def is_empty(self):
        return self.size() == 0