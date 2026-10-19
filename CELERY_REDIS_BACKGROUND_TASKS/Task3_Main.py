from pathlib import Path
from Task3_Tasks import process_file

file_path = Path(__file__).parent / "sample.txt"

task = process_file.delay(
    str(file_path),
    simulate_failures=2,
)

print("Task submitted successfully")
print("Task ID:", task.id)
