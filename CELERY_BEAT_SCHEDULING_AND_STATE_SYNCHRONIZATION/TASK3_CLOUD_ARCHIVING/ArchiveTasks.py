
from datetime import datetime, timezone

from TASK1_CELERY_BEAT_SCHEDULING.CeleryApp import app
from TASK3_CLOUD_ARCHIVING.Storage import archive_file


@app.task(bind=True, name="cloud_archiving.archive_file")
def archive_file_task(self, source_path):
    started_at = datetime.now(timezone.utc).isoformat()

    try:
        archive = archive_file(source_path)

        return {
            "task_id": self.request.id,
            "status": "completed",
            "started_at": started_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            **archive,
        }

    except Exception as exc:
        return {
            "task_id": self.request.id,
            "status": "failed",
            "started_at": started_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "error": str(exc),
        }
