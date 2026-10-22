
import sys

from CeleryApp import app
from TASKS.UploadTasks import upload_log_archives


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "status":
        result = app.AsyncResult(sys.argv[2])

        print(f"Task ID: {result.id}")
        print(f"Status: {result.state}")

        if result.ready():
            print(f"Result: {result.result}")

        return

    result = upload_log_archives.delay()

    print("Upload task submitted successfully.")
    print(f"Task ID: {result.id}")
    print("The Celery worker will process the archives in the background.")


if __name__ == "__main__":
    main()
