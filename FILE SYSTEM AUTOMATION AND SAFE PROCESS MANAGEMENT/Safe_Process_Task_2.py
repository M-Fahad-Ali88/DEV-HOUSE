
import subprocess
import sys


def run_command(arguments):
    try:
        result = subprocess.run(
            arguments,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
            shell=False
        )

        if result.stdout:
            print(result.stdout, end="")

        if result.stderr:
            print(result.stderr, end="")

    except subprocess.CalledProcessError as error:
        print(f"Command failed with exit code {error.returncode}")
        if error.stderr:
            print(error.stderr)

    except subprocess.TimeoutExpired:
        print("Command timed out.")

    except OSError as error:
        print(f"Unable to execute command: {error}")


if __name__ == "__main__":
    run_command([sys.executable, "--version"])