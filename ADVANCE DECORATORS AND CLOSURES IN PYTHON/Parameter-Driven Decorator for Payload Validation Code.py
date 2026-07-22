from functools import wraps


def validate(min_age=18):

    def decorator(func):

        @wraps(func)
        def wrapper(data):

            if not isinstance(data, dict):
                raise TypeError(
                    "Payload must be dictionary"
                )

            if "name" not in data:
                raise ValueError(
                    "Name field missing"
                )

            if "age" not in data:
                raise ValueError(
                    "Age field missing"
                )

            if data["age"] < min_age:
                raise ValueError(
                    f"Minimum age is {min_age}"
                )

            return func(data)

        return wrapper

    return decorator


@validate(min_age=20)
def register(data):
    print("User Registered :", data)


register(
    {
        "name": "Fahad",
        "age": 22
    }
)