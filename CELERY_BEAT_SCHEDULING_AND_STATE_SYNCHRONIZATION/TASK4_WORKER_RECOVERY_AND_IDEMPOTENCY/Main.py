
from TASK4_WORKER_RECOVERY_AND_IDEMPOTENCY.RecoveryTasks import (
    process_operation,
)


def main():
    operation_id = "operation-001"
    result = process_operation.delay(operation_id)

    print(f"Task submitted: {result.id}")
    print(f"Operation ID: {operation_id}")


if __name__ == "__main__":
    main()
