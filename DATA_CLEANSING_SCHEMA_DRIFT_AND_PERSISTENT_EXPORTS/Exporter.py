import csv
import json
from pathlib import Path


OUTPUT_DIR = Path("OUTPUT")


def export_data(records):
    OUTPUT_DIR.mkdir(exist_ok=True)

    export_json(records)
    export_csv(records)


def export_json(records):
    output_file = OUTPUT_DIR / "market_data.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    print(f"JSON exported: {output_file}")


def export_csv(records):
    output_file = OUTPUT_DIR / "market_data.csv"

    if not records:
        return

    fieldnames = [
        "symbol",
        "price",
        "change_percent",
    ]

    with output_file.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(records)

    print(f"CSV exported: {output_file}")