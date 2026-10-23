
from datetime import datetime, timezone

from TASK1_CELERY_BEAT_SCHEDULING.CeleryApp import app
from TASK2_DATABASE_STATE_TRACKING.Database import (
    get_connection,
    initialize_database,
)
from TASK2_DATABASE_STATE_TRACKING.Models import current_timestamp


initialize_database()


def save_task_state(
    task_id,
    task_name,
    status,
    started_at=None,
    completed_at=None,
    error=None,
):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO task_states (
                task_id, task_name, status,
                started_at, completed_at, error
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(task_id) DO UPDATE SET
                status = excluded.status,
                started_at = excluded.started_at,
                completed_at = excluded.completed_at,
                error = excluded.error
            """,
            (
                task_id,
                task_name,
                status,
                started_at,
                completed_at,
                error,
            ),
        )


@app.task(
    bind=True,
    name="state_tracking.process_task",
)
def process_task(self, should_fail=False):
    task_id = self.request.id
    task_name = "process_task"
    started_at = current_timestamp()

    save_task_state(
        task_id,
        task_name,
        "running",
        started_at=started_at,
    )

    try:
        if should_fail:
            raise ValueError("Simulated task failure")

        result = {
            "message": "Task completed successfully",
            "completed_at": current_timestamp(),
        }

        save_task_state(
            task_id,
            task_name,
            "completed",
            started_at=started_at,
            completed_at=result["completed_at"],
        )

        return result

    except Exception as exc:
        save_task_state(
            task_id,
            task_name,
            "failed",
            started_at=started_at,
            completed_at=current_timestamp(),
            error=str(exc),
        )
        raise
