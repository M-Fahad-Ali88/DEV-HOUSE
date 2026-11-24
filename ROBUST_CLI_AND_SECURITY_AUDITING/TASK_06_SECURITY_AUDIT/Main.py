import os
import re
import subprocess
from pathlib import Path
from dotenv import dotenv_values
from rich.console import Console
from rich.table import Table

console = Console()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent

EXCLUDED_DIRS = {".git", ".venv", "__pycache__"}

SECRET_PATTERNS = [
    r"AKIA[0-9A-Z]{16}",
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    r"(?:API_KEY|SECRET_KEY|PASSWORD|ACCESS_TOKEN|AWS_SECRET_ACCESS_KEY)\s*[:=]\s*\S+"
]

def git_command(*args):
    try:
        return subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
    except FileNotFoundError:
        return None

def get_env_files():
    return [
        path for path in PROJECT_ROOT.rglob(".env")
        if not any(part in EXCLUDED_DIRS for part in path.parts)
    ]

def check_git_ignore(path):
    relative_path = path.relative_to(REPO_ROOT)

    result = git_command(
        "check-ignore", "-q", str(relative_path)
    )

    return result is not None and result.returncode == 0

def check_git_tracking(path):
    relative_path = path.relative_to(REPO_ROOT)

    result = git_command(
        "ls-files", "--error-unmatch", str(relative_path)
    )

    return result is not None and result.returncode == 0

def scan_logs(secrets):
    findings = []

    log_files = [
        path for path in PROJECT_ROOT.rglob("*.log")
        if not any(part in EXCLUDED_DIRS for part in path.parts)
    ]

    for file in log_files:
        try:
            content = file.read_text(
                encoding="utf-8",
                errors="replace"
            )

            leaked = any(
                secret in content
                for secret in secrets
                if len(secret) >= 4
            )

            pattern_match = any(
                re.search(pattern, content, re.IGNORECASE)
                for pattern in SECRET_PATTERNS
            )

            if leaked or pattern_match:
                findings.append(file.name)

        except OSError:
            findings.append(file.name + " (unreadable)")

    return findings

def main():

    console.print("\n[bold cyan]SECURITY AUDIT STARTED[/bold cyan]\n")

    table = Table(title="Security Audit Results")

    table.add_column("Security Check", style="cyan")
    table.add_column("Result")

    env_files = get_env_files()

    secrets = [
        value.strip().strip('"').strip("'")
        for value in os.environ.values()
        if value and len(value.strip()) >= 4
    ]

    for env_file in env_files:
        values = dotenv_values(env_file)

        for value in values.values():
            if isinstance(value, str) and len(value) >= 4:
                secrets.append(value)

    env_status = True

    for env_file in env_files:
        ignored = check_git_ignore(env_file)
        tracked = check_git_tracking(env_file)

        if not ignored or tracked:
            env_status = False

    table.add_row(
        ".env Git Protection",
        "[green]PASS[/green]" if env_status
        else "[red]FAIL[/red]"
    )

    if not env_files:
        table.add_row(
            ".env Detection",
            "[yellow]NO .env FILE FOUND[/yellow]"
        )
    else:
        table.add_row(
            ".env Detection",
            "[green]FOUND[/green]"
        )

    log_findings = scan_logs(secrets)

    table.add_row(
        "Log Credential Scan",
        "[green]PASS[/green]" if not log_findings
        else "[red]POTENTIAL LEAK DETECTED[/red]"
    )

    tracked = git_command("ls-files")

    tracked_sensitive = []

    if tracked is not None and tracked.returncode == 0:
        for filename in tracked.stdout.splitlines():
            name = Path(filename).name.lower()

            if name == ".env" or name.endswith(".log"):
                tracked_sensitive.append(filename)

    table.add_row(
        "Tracked Sensitive Files",
        "[green]PASS[/green]" if not tracked_sensitive
        else "[red]REVIEW REQUIRED[/red]"
    )

    console.print(table)

    if log_findings:
        console.print(
            "\n[red]Potential credential leaks found in:[/red]"
        )
        for filename in log_findings:
            console.print(f"[red]- {filename}[/red]")

    if tracked_sensitive:
        console.print(
            "\n[yellow]Sensitive tracked files require review:[/yellow]"
        )
        for filename in tracked_sensitive:
            console.print(filename)

    failed = (
        not env_status
        or bool(log_findings)
        or bool(tracked_sensitive)
    )

    if failed:
        console.print(
            "\n[bold red]SECURITY AUDIT REQUIRES ATTENTION[/bold red]"
        )
    else:
        console.print(
            "\n[bold green]SECURITY CHECKS PASSED[/bold green]"
        )

    console.print(
        "\n[cyan]Audit completed. Review all findings manually.[/cyan]"
    )

if __name__ == "__main__":
    main()
