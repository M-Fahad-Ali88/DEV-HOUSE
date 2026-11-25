import numpy as np
import time

SIZE = 1_000_000

a = list(range(SIZE))
b = list(range(SIZE))
c = list(range(SIZE))

start = time.perf_counter()

python_result = []

for i in range(SIZE):
    python_result.append((a[i] * b[i]) + c[i])

python_time = time.perf_counter() - start

a_np = np.arange(SIZE)
b_np = np.arange(SIZE)
c_np = np.arange(SIZE)

start = time.perf_counter()

numpy_result = (a_np * b_np) + c_np

numpy_time = time.perf_counter() - start

speedup = python_time / numpy_time

print("STANDARD PYTHON TIME:", python_time)
print("NUMPY EXECUTION TIME:", numpy_time)
print("SPEEDUP:", speedup, "x")

print("PYTHON RESULT:", python_result[:5])
print("NUMPY RESULT:", numpy_result[:5])
