from typing import Optional

def add(a:int , b:int) -> int:
    return a+b

def greet(name:str) -> str:
    return f"Hello ,{name}"

def div (a:float , b:float) -> Optional[float]:
    if b == 0:
        return None
    return a/b

def print_message(message:str) -> None:
    print(message)

def main() -> None:
    result = add(10,30)
    print (f"Addition: , {result}")

    greetings = greet("Fahad")
    print(f"Hello",{greetings})

    division = div(20,5)
    print(f"Division: ",{division})

    print_message("I am here to learn python....")

    if __name__ == "__main__":
        main()