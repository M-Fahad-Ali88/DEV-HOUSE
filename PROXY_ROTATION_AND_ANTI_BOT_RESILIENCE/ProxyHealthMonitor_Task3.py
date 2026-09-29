import random
import time


class ProxyHealthMonitor:

    def __init__(self):
        self.proxies = [
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080",
            "http://proxy3.example.com:8080",
        ]

        self.active_proxies = self.proxies.copy()
        self.unhealthy_proxies = {}

    def check_proxy(self, proxy):
        """Simulate a health check for a proxy."""

        # Demo responses:
        # 200 = healthy
        # 429 = rate limited
        # 500 = unhealthy

        status = random.choice([200, 200, 200, 429, 500])

        print(f"\nChecking: {proxy}")
        print(f"Response status: {status}")

        if status == 200:
            return "healthy"

        if status == 429:
            return "rate_limited"

        return "unhealthy"

    def monitor_proxy(self, proxy):
        """Check proxy and update its pool status."""

        status = self.check_proxy(proxy)

        if status == "healthy":
            print("Status: HEALTHY")

            if proxy not in self.active_proxies:
                self.active_proxies.append(proxy)

            self.unhealthy_proxies.pop(proxy, None)

        elif status == "rate_limited":
            print("Status: RATE LIMITED")
            print("Removing proxy temporarily from active pool.")

            if proxy in self.active_proxies:
                self.active_proxies.remove(proxy)

            self.unhealthy_proxies[proxy] = "cooldown"

        else:
            print("Status: UNHEALTHY")
            print("Discarding proxy from active pool.")

            if proxy in self.active_proxies:
                self.active_proxies.remove(proxy)

            self.unhealthy_proxies[proxy] = "unhealthy"

    def run_health_checks(self):
        """Run health checks for all proxies."""

        print("Starting Proxy Health Monitoring...")

        for proxy in self.proxies:
            self.monitor_proxy(proxy)
            time.sleep(1)

        print("\nHealth Check Completed.")

        print("\nActive Proxies:")

        if self.active_proxies:
            for proxy in self.active_proxies:
                print(f"- {proxy}")
        else:
            print("No healthy proxies available.")

        print("\nInactive Proxies:")

        if self.unhealthy_proxies:
            for proxy, reason in self.unhealthy_proxies.items():
                print(f"- {proxy} -> {reason}")
        else:
            print("No inactive proxies.")


if __name__ == "__main__":

    monitor = ProxyHealthMonitor()

    monitor.run_health_checks()