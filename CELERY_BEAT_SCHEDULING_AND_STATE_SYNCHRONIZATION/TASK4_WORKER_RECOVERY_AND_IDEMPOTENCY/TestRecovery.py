
from TASK4_WORKER_RECOVERY_AND_IDEMPOTENCY.RecoveryTasks import (
    process_operation,
)


def main():
    operation_id = "operation-test-001"

    first = process_operation.delay(operation_id)
    second = process_operation.delay(operation_id)

    print(f"First task ID: {first.id}")
    print(f"Second task ID: {second.id}")
    print("Both tasks submitted for idempotency testing.")


if __name__ == "__main__":
    main()
