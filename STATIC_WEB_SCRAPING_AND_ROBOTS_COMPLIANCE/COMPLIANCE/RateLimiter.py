import time


class RateLimiter:
    """
    Controls the minimum delay between HTTP requests.
    """

    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.last_request_time = 0.0

    def wait(self):
        """
        Waits until enough time has passed
        since the previous request.
        """
        elapsed = time.monotonic() - self.last_request_time

        remaining = self.delay - elapsed

        if remaining > 0:
            time.sleep(remaining)

        self.last_request_time = time.monotonic()