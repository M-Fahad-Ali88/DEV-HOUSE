
import shutil
from pathlib import Path


ARCHIVE_DIR = Path(__file__).parent / "ARCHIVE"


def archive_file(source_path):
    source = Path(source_path)

    if not source.is_file():
        raise FileNotFoundError(
            f"Source file not found: {source}"
        )

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    destination = ARCHIVE_DIR / source.name
    shutil.copy2(source, destination)

    return {
        "filename": source.name,
        "storage_path": str(destination.resolve()),
        "size_bytes": destination.stat().st_size,
    }
