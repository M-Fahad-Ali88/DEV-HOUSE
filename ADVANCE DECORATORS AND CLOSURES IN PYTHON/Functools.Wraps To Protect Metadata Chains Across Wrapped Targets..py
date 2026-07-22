def logger(func):
    def wrapper():
        print("Function Started")
        func()
        print("Function Ended")
    return wrapper

@logger
def hello():
    """This is the Hello Function"""
    print("Hello")

hello()
print(hello.__name__)
print(hello.__doc__)