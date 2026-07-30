import multiprocessing


def increment(counter):
    for _ in range(100000):
        counter.value += 1


def increment_safe(counter, lock):
    for _ in range(100000):
        with lock:
            counter.value += 1


if __name__ == "__main__":

    print("Without Lock")

    counter = multiprocessing.Value('i', 0)

    p1 = multiprocessing.Process(target=increment, args=(counter,))
    p2 = multiprocessing.Process(target=increment, args=(counter,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("Counter:", counter.value)

    print()

    print("With Lock")

    counter = multiprocessing.Value('i', 0)
    lock = multiprocessing.Lock()

    p1 = multiprocessing.Process(target=increment_safe, args=(counter, lock))
    p2 = multiprocessing.Process(target=increment_safe, args=(counter, lock))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("Counter:", counter.value)