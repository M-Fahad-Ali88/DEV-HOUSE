import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import requests

def fetch_url(url):
    response = requests.get(url)
    return f"{url} -> {response.status_code}"

if __name__ == "__main__":
    urls = [
        "https://httpbin.org/delay/2",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/delay/2"
    ]

    start = time.time()
    #results = [fetch_url(url) for url in urls]
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch_url, urls))
    end = time.time()
    print(f"Results:  {results}")
    print(f"Single-Threaded time: {end - start:.2f} seconds")

    start_time = time.time()

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch_url, urls))

    end_time = time.time()
    print(f"Results:  {results}")
    print(f"Threaded time: {end_time - start_time:.2f} seconds")
def sum_of_squares(n):
    return sum(i*i for i in range(n))

if __name__ == "__main__":
    numbers = [10_000_000,20_000_000,30_000_000,40_000_000]
    start_time = time.time()

    with ProcessPoolExecutor() as executor:
         results = list(executor.map(sum_of_squares, numbers))

    end_time = time.time()
    print(f"Results:  {results}")
    print(f"Single-Threaded time: {end_time - start_time:.2f} seconds")