from celery import Celery
from Config import REDIS_URL

app = Celery(
    "scheduled_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "TASK1_CELERY_BEAT_SCHEDULING.ScheduledTasks",
        "TASK2_DATABASE_STATE_TRACKING.StateTasks",
        "TASK3_CLOUD_ARCHIVING.ArchiveTasks",
        "TASK4_WORKER_RECOVERY_AND_IDEMPOTENCY.RecoveryTasks",
    ],
)

app.conf.update(
    timezone="Asia/Karachi",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_transport_options={"visibility_timeout": 30},
    result_backend_transport_options={"visibility_timeout": 30},
    visibility_timeout=30,
    beat_schedule={
        "cleanup-logs-every-minute": {
            "task": "scheduled_tasks.cleanup_logs",
            "schedule": 60.0,
        },
    },
)
