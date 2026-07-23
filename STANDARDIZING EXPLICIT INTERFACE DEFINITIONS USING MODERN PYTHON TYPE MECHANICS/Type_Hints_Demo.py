from typing import TypeVar, Callable


T = TypeVar("T")


def first_item(items: list[T]) -> T:
    return items[0]



def square(number: int | float) -> int | float:
    return number * number



def greet(name: str | None) -> str:
    if name is None:
        return "Hello Guest"
    return f"Hello {name}"



def add(x: int, y: int) -> int:
    return x + y


def multiply(x: int, y: int) -> int:
    return x * y


def calculate(
    a: int,
    b: int,
    operation: Callable[[int, int], int]
) -> int:
    return operation(a, b)



numbers = [10, 20, 30]
names = ["Ali", "Ahmed", "Sara"]

print("===== GENERICS =====")
print(first_item(numbers))
print(first_item(names))

print("\n===== UNION =====")
print(square(5))
print(square(3.5))

print("\n===== OPTIONAL =====")
print(greet("Fahad"))
print(greet(None))

print("\n===== CALLABLE =====")
print(calculate(10, 20, add))
print(calculate(10, 20, multiply))