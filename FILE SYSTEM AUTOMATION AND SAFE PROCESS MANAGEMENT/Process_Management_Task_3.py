
import subprocess
import sys

process = subprocess.Popen(
    [
        sys.executable,
        "-c",
        "import time; time.sleep(60)"
    ],
    shell=False
)

print(f"Process ID: {process.pid}")

try:
    process.wait(timeout=3)
    print("Process completed normally.")

except subprocess.TimeoutExpired:
    print("Process exceeded the time limit.")
    process.terminate()
    process.wait()
    print("Process terminated successfully.")

print(f"Exit code: {process.returncode}")