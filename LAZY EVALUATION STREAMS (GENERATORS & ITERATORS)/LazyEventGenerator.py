import sys


def event_generator(limit):
    for i in range(limit):
        yield f"Event Log {i + 1}"


limit = 1_000_000

generator = event_generator(limit)
event_list = [f"Event Log {i + 1}" for i in range(limit)]

print("Generator Memory:", sys.getsizeof(generator), "bytes")
print("List Memory:", sys.getsizeof(event_list), "bytes")

print("\nFirst 5 Generator Events:")
for _ in range(5):
    print(next(generator))