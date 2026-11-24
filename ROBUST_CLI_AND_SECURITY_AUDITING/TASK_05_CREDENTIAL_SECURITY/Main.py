import os
import logging
from dotenv import load_dotenv
from rich.console import Console

console = Console()

load_dotenv()

logging.basicConfig(
    filename="secure_application.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("SECURITY")

api_key = os.getenv("API_KEY")
database_password = os.getenv("DATABASE_PASSWORD")
aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")

def mask_secret(secret):
    if not secret:
        return "NOT CONFIGURED"

    return "*" * 8

console.print("[bold cyan]SECURITY CONFIGURATION CHECK[/bold cyan]")

secrets = {
    "API KEY": api_key,
    "DATABASE PASSWORD": database_password,
    "AWS SECRET": aws_secret
}

for name, value in secrets.items():
    if value:
        console.print(f"[green]{name}: CONFIGURED[/green]")
        logger.info("%s configured successfully", name)
    else:
        console.print(f"[yellow]{name}: NOT CONFIGURED[/yellow]")
        logger.warning("%s is missing", name)

console.print("\n[bold green]Credential security check completed![/bold green]")
