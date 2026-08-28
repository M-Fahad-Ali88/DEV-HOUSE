import time
import requests
from concurrent.futures import ThreadPoolExecutor


FASTAPI_URL = "http://127.0.0.1:8000/async"
FLASK_URL = "http://127.0.0.1:5000/sync"

REQUESTS = 50
CONCURRENCY = 10


def send_request(url):
    start = time.perf_counter()

    response = requests.get(url)

    elapsed = time.perf_counter() - start

    return response.status_code, elapsed


def benchmark(name, url):
    print(f"\n{name}")
    print("-" * 40)

    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        results = list(
            executor.map(
                send_request,
                [url] * REQUESTS
            )
        )

    total_time = time.perf_counter() - start

    successful = sum(
        1 for status, _ in results
        if status == 200
    )

    average_time = sum(
        elapsed for _, elapsed in results
    ) / len(results)

    throughput = REQUESTS / total_time

    print(f"Requests: {REQUESTS}")
    print(f"Concurrency: {CONCURRENCY}")
    print(f"Successful: {successful}")
    print(f"Total Time: {total_time:.2f} seconds")
    print(f"Average Response: {average_time:.2f} seconds")
    print(f"Throughput: {throughput:.2f} requests/sec")


if __name__ == "__main__":
    benchmark("FASTAPI ASYNC", FASTAPI_URL)
    benchmark("FLASK SYNC", FLASK_URL)