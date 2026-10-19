
import sys
from celery.result import AsyncResult
from Task3_Tasks import app

if len(sys.argv) != 2:
    print("Usage: python Task2_CheckStatus.py <task_id>")
    raise SystemExit(1)

task = AsyncResult(sys.argv[1], app=app)

print("Task ID:", task.id)
print("Current state:", task.state)

if task.successful():
    print("Task completed successfully")
    print("Result:", task.result)
elif task.failed():
    print("Task failed")
    print("Error:", task.result)
elif task.state == "RETRY":
    print("Task is waiting for a retry")
else:
    print("Task has not completed yet")
