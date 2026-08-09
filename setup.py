#!/usr/bin/env python3
"""
Scheduler Setup for GitHub Streak Maintainer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Creates (or removes) Windows Scheduled Tasks that run auto_commit.py
at every time listed in config.json → push_times.

Usage
-----
  python setup.py            # Create / recreate all tasks
  python setup.py --remove   # Remove all streak tasks
  python setup.py --status   # Show current task status

Requires Administrator privileges to create tasks.
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / "config.json"
AUTO_COMMIT = SCRIPT_DIR / "auto_commit.py"
TASK_PREFIX = "GitHubStreakMaintainer"
MAX_TASKS = 24  # hard ceiling for cleanup sweeps


def load_push_times() -> list[str]:
    """Read push_times from config.json (fall back to 3 defaults)."""
    defaults = ["09:00", "14:00", "21:00"]
    if not CONFIG_FILE.exists():
        return defaults
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh).get("push_times", defaults)
    except (json.JSONDecodeError, OSError):
        return defaults


def remove_all_tasks() -> int:
    """Delete every GitHubStreakMaintainer_* task. Returns count removed."""
    removed = 0
    # Remove numbered tasks
    for i in range(1, MAX_TASKS + 1):
        name = f"{TASK_PREFIX}_{i}"
        r = subprocess.run(
            ["schtasks", "/delete", "/tn", name, "/f"],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            removed += 1
    # Also remove a legacy un-numbered task if it exists
    r = subprocess.run(
        ["schtasks", "/delete", "/tn", TASK_PREFIX, "/f"],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        removed += 1
    return removed


def create_tasks(push_times: list[str]) -> list[tuple[str, str, bool, str]]:
    """
    Create one scheduled task per push time.
    Returns [(task_name, time, success, message), ...].
    """
    python_exe = sys.executable
    results = []

    for idx, time_str in enumerate(push_times, start=1):
        name = f"{TASK_PREFIX}_{idx}"
        cmd = [
            "schtasks", "/create",
            "/tn", name,
            "/tr", f'"{python_exe}" "{AUTO_COMMIT}"',
            "/sc", "daily",
            "/st", time_str,
            "/rl", "highest",
            "/f",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        ok = r.returncode == 0
        msg = r.stdout.strip() if ok else r.stderr.strip()
        results.append((name, time_str, ok, msg))

    return results


def query_tasks() -> None:
    """Print the status of all GitHubStreakMaintainer tasks."""
    found = False
    for i in range(1, MAX_TASKS + 1):
        name = f"{TASK_PREFIX}_{i}"
        r = subprocess.run(
            ["schtasks", "/query", "/tn", name, "/fo", "LIST"],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            found = True
            print(r.stdout)
    if not found:
        print("No GitHubStreakMaintainer tasks found.")
        print("Run  python setup.py  to create them.")


# ==============================  CLI  =====================================


def main() -> None:
    # ---- Flags ----
    if "--remove" in sys.argv:
        print("Removing all scheduled tasks...")
        n = remove_all_tasks()
        print(f"Done — {n} task(s) removed.")
        return

    if "--status" in sys.argv:
        query_tasks()
        return

    # ---- Create / recreate ----
    push_times = load_push_times()

    print("=" * 55)
    print("  GitHub Streak Maintainer — Scheduler Setup")
    print("=" * 55)
    print()
    print(f"  Python  : {sys.executable}")
    print(f"  Script  : {AUTO_COMMIT}")
    print(f"  Times   : {', '.join(push_times)}")
    print()

    # Clean slate
    removed = remove_all_tasks()
    if removed:
        print(f"  Cleaned up {removed} old task(s).\n")

    # Create new tasks
    print("  Creating tasks:")
    results = create_tasks(push_times)

    ok_count = 0
    for name, time_str, ok, msg in results:
        icon = "\u2705" if ok else "\u274c"
        print(f"    {icon}  {name}  →  daily at {time_str}")
        if not ok:
            print(f"        Error: {msg}")
        else:
            ok_count += 1

    print()
    print(f"  Result: {ok_count}/{len(results)} tasks created.")

    if ok_count < len(results):
        print()
        print("  \u26a0  Some tasks failed. Make sure you're running as Administrator:")
        print("     Right-click Terminal → Run as Administrator")
        print(f'     cd "{SCRIPT_DIR}"')
        print("     python setup.py")

    print()
    print("  \u2139  Edit config.json → push_times to change the schedule,")
    print("     then re-run this script.")
    print()


if __name__ == "__main__":
    main()
