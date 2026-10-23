
from pathlib import Path

from TASK3_CLOUD_ARCHIVING.ArchiveTasks import archive_file_task


SAMPLE_FILE = Path(__file__).parent / "sample.txt"


def main():
    if not SAMPLE_FILE.exists():
        SAMPLE_FILE.write_text(
            "This file is used to test background cloud archiving.",
            encoding="utf-8",
        )

    result = archive_file_task.delay(str(SAMPLE_FILE.resolve()))

    print(f"Archive task submitted: {result.id}")


if __name__ == "__main__":
    main()
