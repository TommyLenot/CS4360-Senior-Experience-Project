from src.ingestion.queue import AlertQueue


class AlertHandoff:
    def __init__(self, queue):
        if not isinstance(queue, AlertQueue):
            raise TypeError(
                "queue must be an AlertQueue."
            )

        self.queue = queue

    def get_next_pending(self):
        pending_alerts = self.queue.get_pending_alerts()

        if not pending_alerts:
            return None

        return pending_alerts[0]

    def get_next_pending_dict(self):
        alert = self.get_next_pending()

        if alert is None:
            return None

        return alert.to_dict()

    def get_pending_count(self):
        return len(
            self.queue.get_pending_alerts()
        )

    def has_pending_alerts(self):
        return self.get_pending_count() > 0