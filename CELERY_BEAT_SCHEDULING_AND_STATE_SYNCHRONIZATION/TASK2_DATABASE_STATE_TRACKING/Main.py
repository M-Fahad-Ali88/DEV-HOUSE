
from TASK2_DATABASE_STATE_TRACKING.Database import (
    get_connection,
    initialize_database,
)
from TASK2_DATABASE_STATE_TRACKING.StateTasks import process_task


def main():
    initialize_database()

    result = process_task.delay()

    print(f"Task submitted successfully: {result.id}")


if __name__ == "__main__":
    main()
