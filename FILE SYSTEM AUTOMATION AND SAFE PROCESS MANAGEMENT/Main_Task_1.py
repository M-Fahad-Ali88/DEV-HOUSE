
from pathlib import Path
from datetime import datetime, timedelta

TARGET_DIRECTORY = Path("LOGS")
STALE_DAYS = 30


def analyze_files(directory):
    if not directory.exists() or not directory.is_dir():
        print(f"Invalid directory: {directory}")
        return

    cutoff_time = datetime.now().timestamp() - timedelta(days=STALE_DAYS).total_seconds()

    for file in directory.rglob("*"):
        try:
            if not file.is_file():
                continue

            metadata = file.stat()
            modified_time = datetime.fromtimestamp(metadata.st_mtime)

            print(f"File: {file}")
            print(f"Size: {metadata.st_size} bytes")
            print(f"Last Modified: {modified_time:%Y-%m-%d %H:%M:%S}")

            if file.suffix.lower() == ".log" and metadata.st_mtime < cutoff_time:
                print("Status: STALE LOG FILE")

            print("-" * 40)

        except (OSError, PermissionError) as error:
            print(f"Cannot access {file}: {error}")


if __name__ == "__main__":
    analyze_files(TARGET_DIRECTORY)