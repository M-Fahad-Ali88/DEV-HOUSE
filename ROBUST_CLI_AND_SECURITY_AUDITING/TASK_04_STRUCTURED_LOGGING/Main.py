import logging
from rich.console import Console

console = Console()

logging.basicConfig(
    filename="application.log",
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("CLI_AUDIT")

console.print("[bold cyan]CLI SYSTEM AUDIT[/bold cyan]")

logger.info("Application started")
console.print("[green]Application started[/green]")

logger.debug("Initializing application components")

logger.info("Configuration loaded successfully")
console.print("[green]Configuration loaded[/green]")

try:
    number = 10
    result = number / 2

    logger.info("Calculation completed successfully")
    console.print(f"[green]Calculation result: {result}[/green]")

except Exception:
    logger.exception("Calculation failed")
    console.print("[red]An unexpected error occurred[/red]")

logger.warning("Application is preparing to shut down")

logger.info("Application stopped")

console.print("[bold green]Audit logging completed![/bold green]")
