import time 
import sqlite3
from pathlib import Path

from TASK1_CELERY_BEAT_SCHEDULING.CeleryApp import app


DATABASE_PATH = Path(__file__).parent / "operations.db"


def initialize_database():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS completed_operations (
                operation_id TEXT PRIMARY KEY,
                completed_at TEXT NOT NULL
            )
            """
        )


def is_processed(operation_id):
    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            "SELECT 1 FROM completed_operations WHERE operation_id = ?",
            (operation_id,),
        ).fetchone()

    return row is not None


def mark_processed(operation_id):
    from datetime import datetime, timezone

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO completed_operations
            (operation_id, completed_at)
            VALUES (?, ?)
            """,
            (operation_id, datetime.now(timezone.utc).isoformat()),
        )


initialize_database()


@app.task(
    bind=True,
    name="recovery.process_operation",
    max_retries=3,
    default_retry_delay=5,
)
def process_operation(self, operation_id, should_fail=False):
    if is_processed(operation_id):
        return {
            "status": "already_processed",
            "operation_id": operation_id,
        }

    try:
        if should_fail:
            raise ValueError("Simulated temporary failure")

        mark_processed(operation_id)

        return {
            "status": "completed",
            "operation_id": operation_id,
        }

    except ValueError as exc:
        if self.request.retries < 3:
            raise self.retry(exc=exc, countdown=5)

        raise




@app.task(name="recovery.crash_recovery_test")
def crash_recovery_test(operation_id):
    if is_processed(operation_id):
        return {
            "status": "already_processed",
            "operation_id": operation_id,
        }

    print(f"Starting recovery test: {operation_id}", flush=True)
    time.sleep(60)

    mark_processed(operation_id)

    return {
        "status": "completed",
        "operation_id": operation_id,
    }
