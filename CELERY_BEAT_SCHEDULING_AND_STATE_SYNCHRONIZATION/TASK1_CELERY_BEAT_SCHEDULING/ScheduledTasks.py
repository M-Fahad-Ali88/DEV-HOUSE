
from datetime import datetime, timedelta, timezone
from pathlib import Path

from Config import LOG_DIR, LOG_RETENTION_DAYS
from TASK1_CELERY_BEAT_SCHEDULING.CeleryApp import app


@app.task(name="scheduled_tasks.cleanup_logs")
def cleanup_logs():
    log_dir = Path(LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    cutoff = datetime.now(timezone.utc) - timedelta(
        days=LOG_RETENTION_DAYS
    )

    deleted = 0

    for file in log_dir.glob("*.log"):
        modified = datetime.fromtimestamp(
            file.stat().st_mtime,
            tz=timezone.utc,
        )

        if modified < cutoff:
            file.unlink()
            deleted += 1

    return {
        "status": "completed",
        "deleted_files": deleted,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
