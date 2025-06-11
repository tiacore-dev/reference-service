from prometheus_client import Counter


class AnalysisMetrics:
    def __init__(self):
        self.success_counter = Counter(
            "analysis_success_total",
            "Успешные запуски анализа",
            ["chat_id", "schedule_id"]
        )

        self.failed_counter = Counter(
            "analysis_failed_total",
            "Проваленные запуски анализа",
            ["chat_id", "schedule_id"]
        )

    def inc_success(self, chat_id: str, schedule_id: str):
        self.success_counter.labels(
            chat_id=chat_id, schedule_id=schedule_id).inc()

    def inc_failure(self, chat_id: str, schedule_id: str):
        self.failed_counter.labels(
            chat_id=chat_id, schedule_id=schedule_id).inc()
