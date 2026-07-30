import threading
import multiprocessing
import time


def heavy_math():
    total = 0
    for i in range(25_000_000):
        total += i * i


def run_threads():
    start = time.perf_counter()

    t1 = threading.Thread(target=heavy_math)
    t2 = threading.Thread(target=heavy_math)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("Threading Time:", time.perf_counter() - start)


def run_processes():
    start = time.perf_counter()

    p1 = multiprocessing.Process(target=heavy_math)
    p2 = multiprocessing.Process(target=heavy_math)

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("Multiprocessing Time:", time.perf_counter() - start)


if __name__ == "__main__":
    run_threads()
    run_processes()