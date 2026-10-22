
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import zipfile

from CeleryApp import app
from STORAGE.S3Client import upload_archive

PROJECT_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_DIR / "LOGS"
ARCHIVE_DIR = PROJECT_DIR / "ARCHIVES"


def compress_log(log_path):
    ARCHIVE_DIR.mkdir(exist_ok=True)

    archive_path = ARCHIVE_DIR / f"{log_path.stem}.zip"

    with zipfile.ZipFile(
        archive_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        archive.write(log_path, arcname=log_path.name)

    return str(archive_path)


@app.task(
    bind=True,
    name="TASKS.UploadTasks.upload_log_archives",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def upload_log_archives(self):
    log_files = list(LOG_DIR.glob("*.log"))

    if not log_files:
        raise FileNotFoundError(f"No .log files found in {LOG_DIR}")

    archives = [compress_log(path) for path in log_files]
    results = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(upload_archive, path): path
            for path in archives
        }

        for future in as_completed(futures):
            results.append(future.result())

    return {
        "status": "SUCCESS",
        "uploaded_count": len(results),
        "uploads": results,
    }
