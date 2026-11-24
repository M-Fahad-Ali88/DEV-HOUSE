import time
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn

with Progress(
    SpinnerColumn(),
    TextColumn("[bold cyan]{task.description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    TimeElapsedColumn(),
    TimeRemainingColumn()
) as progress:

    task = progress.add_task("Processing data...", total=100)

    for i in range(100):
        time.sleep(0.05)
        progress.update(task, advance=1)

print("Processing completed successfully!")
