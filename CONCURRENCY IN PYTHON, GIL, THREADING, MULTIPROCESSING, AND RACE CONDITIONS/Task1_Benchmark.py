import threading
import multiprocessing
import time


def cpu_task():
    total = 0
    for i in range(15_000_000):
        total += i * i



def io_task():
    time.sleep(2)


def benchmark(name, target, mode):
    start = time.perf_counter()

    workers = []

    if mode == "single":
        for _ in range(4):
            target()

    elif mode == "thread":
        for _ in range(4):
            t = threading.Thread(target=target)
            workers.append(t)
            t.start()

        for t in workers:
            t.join()

    elif mode == "process":
        for _ in range(4):
            p = multiprocessing.Process(target=target)
            workers.append(p)
            p.start()

        for p in workers:
            p.join()

    end = time.perf_counter()

    print(f"{name:<35} {mode:<10} {end-start:.2f} seconds")


if __name__ == "__main__":

    print("CPU Bound Benchmark")
    benchmark("CPU", cpu_task, "single")
    benchmark("CPU", cpu_task, "thread")
    benchmark("CPU", cpu_task, "process")

    print()

    print("IO Bound Benchmark")
    benchmark("IO", io_task, "single")
    benchmark("IO", io_task, "thread")
    benchmark("IO", io_task, "process")