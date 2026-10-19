from pathlib import Path
from Task1_Tasks import process_file

file_path = Path(__file__).parent / "sample.txt"

task = process_file.delay(str(file_path))

print("Task submitted successfully")
print("Task ID:", task.id)
