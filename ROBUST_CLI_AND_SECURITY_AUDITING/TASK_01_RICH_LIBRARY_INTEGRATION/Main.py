from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

console.print("[bold green]Welcome to CLI Security Tool![/bold green]")

console.print("[yellow]Initializing application...[/yellow]")

console.print(
    Panel(
        "CLI application initialized successfully.",
        title="SYSTEM STATUS",
        border_style="green"
    )
)

table = Table(title="Application Information")

table.add_column("Component", style="cyan")
table.add_column("Status", style="green")

table.add_row("Rich Library", "Installed")
table.add_row("CLI Interface", "Active")
table.add_row("Application", "Running")

console.print(table)

console.print("[bold green]Task completed successfully![/bold green]")
