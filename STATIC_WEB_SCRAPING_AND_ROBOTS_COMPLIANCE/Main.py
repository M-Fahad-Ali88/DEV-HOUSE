from pathlib import Path

import requests

from COMPLIANCE.RobotsChecker import RobotsChecker
from EXTRACTORS.StockTableExtractor import StockTableExtractor
from COMPLIANCE.RateLimiter import RateLimiter

def parse_local_stock_page():
    """
    Tests the BeautifulSoup extractor using
    our local static HTML file.
    """
    html_path = Path("TEST_DATA/StockPage.html")

    html = html_path.read_text(encoding="utf-8")

    extractor = StockTableExtractor()

    stocks = extractor.extract(html)

    print("\nLOCAL STOCK DATA")
    print("-" * 50)

    for stock in stocks:
        print(stock)


def check_robots(url: str):
    """
    Checks robots.txt before allowing crawling.
    """
    checker = RobotsChecker()

    print("\nROBOTS.TXT COMPLIANCE")
    print("-" * 50)
    print(f"Checking: {url}")

    if checker.can_fetch(url):
        print("Crawling is allowed.")
    else:
        print("Crawling is not allowed.")

def test_rate_limiter():
    """
    Demonstrates controlled delays between requests.
    """
    limiter = RateLimiter(delay=2.0)

    print("\nRATE LIMITER TEST")
    print("-" * 50)

    for request_number in range(1, 4):
        limiter.wait()

        print(f"Request {request_number} sent.")

def handle_response(response):
    """
    Handles HTTP responses, especially rate limiting.
    """
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After")

        print("Server rate limit reached.")

        if retry_after:
            print(f"Retry after: {retry_after} seconds.")
        else:
            print("Retry-After header was not provided.")

        return False

    response.raise_for_status()

    return True

def fetch_remote_stock_page(url: str):
    """
    Checks robots.txt before making a downstream
    HTTP request.
    """
    checker = RobotsChecker()

    if not checker.can_fetch(url):
        print("Crawling is not allowed.")
        return

    print("Crawling is allowed.")

    response = requests.get(
        url,
        headers={
            "User-Agent": "DistributedFinancialEngine/1.0"
        },
        timeout=10,
    )

    response.raise_for_status()

    extractor = StockTableExtractor()

    stocks = extractor.extract(response.text)

    print("\nREMOTE STOCK DATA")
    print("-" * 50)

    for stock in stocks:
        print(stock)


def main():
    # Task 1: Static HTML parsing
    parse_local_stock_page()

    # Task 2: robots.txt compliance
    check_robots("https://example.com/")

    # Task 3: Rate limiting
    test_rate_limiter()

    print("\nHTTP 429 HANDLING")
    print("-" * 50)
    print("429 handler is ready.")

if __name__ == "__main__":
    main()