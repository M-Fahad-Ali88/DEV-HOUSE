from TASK4_WORKER_RECOVERY_AND_IDEMPOTENCY.RecoveryTasks import (
    crash_recovery_test,
)


def main():
    operation_id = "operation-crash-005"
    result = crash_recovery_test.delay(operation_id)

    print(f"Task ID: {result.id}")
    print(f"Operation ID: {operation_id}")


if __name__ == "__main__":
    main()
