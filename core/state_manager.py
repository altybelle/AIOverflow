class StateManager:
    def __init__(self):
        self.backoff = 0
        self.quota_remaining = 10_000
        self.condition = threading.Condition()

    def update_backoff(self, backoff_time):
        with self.condition:
            self.backoff = backoff_time
            self.condition.notify_all()

    def wait_for_backoff(self):
        with self.condition:
            while self.backoff > 0:
                self.condition.wait()

    def update_quota(self, quota):
        with self.condition:
            self.quota_remaining = quota

    def has_quota(self):
        return self.quota_remaining > 0
