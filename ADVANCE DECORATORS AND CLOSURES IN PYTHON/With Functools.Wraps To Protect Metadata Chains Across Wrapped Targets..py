from functools import wraps


def logger(func):

    @wraps(func)
    def wrapper():
        print("Function Started")
        func()
        print("Function Ended")

    return wrapper


@logger
def hello():
    """This is hello function"""
    print("Hello")


hello()

print(hello.__name__)
print(hello.__doc__)