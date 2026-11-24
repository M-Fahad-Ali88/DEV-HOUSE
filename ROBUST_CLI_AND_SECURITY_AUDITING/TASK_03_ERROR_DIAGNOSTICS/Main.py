from rich.console import Console
from rich.panel import Panel
from rich.traceback import install

console = Console()

install(show_locals=False)

def divide_numbers(a, b):
    try:
        result = a / b
        console.print(f"[bold green]Result: {result}[/bold green]")

    except ZeroDivisionError:
        console.print(
            Panel(
                "Division by zero is not allowed.",
                title="INPUT ERROR",
                border_style="red"
            )
        )

    except TypeError:
        console.print(
            "[bold red]Error: Please provide valid numbers.[/bold red]"
        )

    except Exception as error:
        console.print(
            f"[bold red]Unexpected error: {type(error).__name__}[/bold red]"
        )

console.print("[bold cyan]CLI Error Diagnostics[/bold cyan]")

try:
    first = float(input("Enter first number: "))
    second = float(input("Enter second number: "))

    divide_numbers(first, second)

except ValueError:
    console.print(
        Panel(
            "Invalid input. Please enter numeric values.",
            title="VALIDATION ERROR",
            border_style="yellow"
        )
    )
