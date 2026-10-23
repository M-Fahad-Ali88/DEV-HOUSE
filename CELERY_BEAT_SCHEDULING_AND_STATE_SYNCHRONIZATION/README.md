# Celery Beat Scheduling and State Synchronization

A Python project demonstrating periodic task scheduling, task-state tracking, local file archiving, retry handling, idempotency, and worker crash recovery.

## Technologies

- Python
- Celery
- Redis
- SQLite
- PowerShell
- Local file storage

All components are designed to run locally without requiring paid cloud services.

## Project Tasks

### Task 1: Celery Beat Scheduling
Schedules periodic log cleanup using Celery Beat.

### Task 2: Database State Tracking
Stores task execution states and failure information in SQLite.

### Task 3: Cloud Archiving Simulation
Copies files into a local archive directory. This demonstrates the archiving workflow but does not upload files to an actual cloud provider.

### Task 4: Worker Recovery and Idempotency
Implements task retries and persistent operation tracking using SQLite.

### Task 5: Crash Recovery Testing
Tests task redelivery after forcibly stopping and restarting the Celery worker. The local test successfully redelivered the same task ID and completed the task.

### Task 6: Final Project Verification
Checks Python syntax, Celery task registration, database files, and archive output.

## Project Structure

- `TASK1_CELERY_BEAT_SCHEDULING/` — Celery application, scheduled tasks, and logs
- `TASK2_DATABASE_STATE_TRACKING/` — SQLite task-state tracking
- `TASK3_CLOUD_ARCHIVING/` — local file archiving
- `TASK4_WORKER_RECOVERY_AND_IDEMPOTENCY/` — retries, idempotency, and crash recovery tests
- `Config.py` — shared configuration
- `requirements.txt` — Python dependencies

## Setup

Activate the existing virtual environment:

```powershell
& "D:\DEV HOUSE\Python\.venv\Scripts\Activate.ps1"
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Ensure Redis is running locally before starting Celery.

## Start the Celery Worker

Run from the project root:

```powershell
celery -A TASK1_CELERY_BEAT_SCHEDULING.CeleryApp:app worker --loglevel=info --pool=solo
```

## Start Celery Beat

Open a separate terminal:

```powershell
celery -A TASK1_CELERY_BEAT_SCHEDULING.CeleryApp:app beat --loglevel=info
```

Run only one Beat scheduler instance using the same schedule file.

## Run the Tests

Run these commands from the project root with the virtual environment activated:

```powershell
python -m TASK2_DATABASE_STATE_TRACKING.Main
python -m TASK3_CLOUD_ARCHIVING.Main
python -m TASK4_WORKER_RECOVERY_AND_IDEMPOTENCY.Main
python -m TASK4_WORKER_RECOVERY_AND_IDEMPOTENCY.TestRecovery
python -m TASK4_WORKER_RECOVERY_AND_IDEMPOTENCY.TestCrashRecovery
```

The crash recovery test requires a running worker and Redis.

## Local Data

- `TASK2_DATABASE_STATE_TRACKING/task_states.db` — task-state records
- `TASK4_WORKER_RECOVERY_AND_IDEMPOTENCY/operations.db` — processed-operation records
- `TASK3_CLOUD_ARCHIVING/ARCHIVE/` — archived files
- `celerybeat-schedule.*` — Celery Beat scheduler state

## Limitations

This project is intended for local learning and testing. SQLite and local file storage do not replace a production distributed database or a cloud storage provider.