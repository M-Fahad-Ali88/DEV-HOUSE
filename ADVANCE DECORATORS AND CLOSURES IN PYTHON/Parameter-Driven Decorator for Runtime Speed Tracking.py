import time
from functools import wraps


def timer(unit="ms"):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            start = time.time()

            result = func(*args, **kwargs)

            end = time.time()

            elapsed = end - start

            if unit == "ms":
                elapsed *= 1000
                print(
                    f"{func.__name__} executed in "
                    f"{elapsed:.2f} ms"
                )
            else:
                print(
                    f"{func.__name__} executed in "
                    f"{elapsed:.4f} sec"
                )

            return result

        return wrapper

    return decorator


@timer("ms")
def calculate():

    total = 0

    for i in range(100000):
        total += i

    return total


calculate()