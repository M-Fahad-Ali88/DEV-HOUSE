import random


class ProxyMiddleware:

    def __init__(self):
        self.proxies = [
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080",
            "http://proxy3.example.com:8080",
        ]

        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36",

            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) "
            "Gecko/20100101 Firefox/143.0",

            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36",
        ]

    def get_proxy(self):
        """Select an available proxy from the proxy pool."""
        return random.choice(self.proxies)

    def get_headers(self):
        """Generate custom request headers."""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://example.com/",
        }

    def prepare_request(self):
        """Prepare proxy and headers for a request."""
        proxy = self.get_proxy()
        headers = self.get_headers()

        return {
            "proxy": proxy,
            "headers": headers,
        }


if __name__ == "__main__":
    middleware = ProxyMiddleware()

    request_config = middleware.prepare_request()

    print("Selected Proxy:")
    print(request_config["proxy"])

    print("\nRequest Headers:")
    for key, value in request_config["headers"].items():
        print(f"{key}: {value}")