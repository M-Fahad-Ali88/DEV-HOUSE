import time

def sum_of_squares(n):
    return sum(i*i for i in range(n))

if __name__== "__main__":
    numbers = [10_000_000, 20_000_000, 30_000_000, 40_000_000]
    start_time= time.time()
    results = [sum_of_squares(n) for n in numbers]
    end_time = time.time()
    print(f"Results:  {results}")
    print(f"Single-Threaded time: {end_time - start_time:.2f} seconds")  
