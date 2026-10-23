
from TASK1_CELERY_BEAT_SCHEDULING.ScheduledTasks import cleanup_logs


if __name__ == "__main__":
    result = cleanup_logs.delay()
    print(f"Task submitted successfully: {result.id}")
