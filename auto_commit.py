#!/usr/bin/env python3
"""
Automatic GitHub Streak Maintainer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Appends a timestamped entry to streak.json, commits the change,
and pushes to GitHub. Designed to be run by Windows Task Scheduler
multiple times per day.
"""

import json
import os
import subprocess
import sys
import random
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths — always resolve relative to this script so Task Scheduler works
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / "config.json"
STREAK_FILE = SCRIPT_DIR / "streak.json"
LOG_DIR = SCRIPT_DIR / "logs"
LOG_FILE = LOG_DIR / "auto_commit.log"

# ---------------------------------------------------------------------------
# Motivational quotes — picked at random for each commit message
# ---------------------------------------------------------------------------
QUOTES = [
    "Consistency is the key to mastery.",
    "One commit at a time.",
    "The streak lives on!",
    "Code every day, grow every day.",
    "Small steps, big results.",
    "Keep the green squares alive!",
    "Another day, another commit.",
    "Building habits, one push at a time.",
    "The best time to code was yesterday. The next best time is now.",
    "Discipline equals freedom.",
    "Show up every day.",
    "Progress, not perfection.",
    "Every expert was once a beginner.",
    "Stay consistent, stay committed.",
    "The journey of a thousand commits begins with a single push.",
    "Push it. Ship it. Repeat.",
    "Green squares don't grow on trees — they grow on discipline.",
    "Streak mode: activated.",
    "Today's commit is tomorrow's habit.",
    "Commit to the process, not just the outcome.",
]


# ===========================  HELPERS  ====================================


def log(message: str) -> None:
    """Write a timestamped message to stdout *and* the log file."""
    LOG_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def load_config() -> dict:
    """Return the contents of config.json, falling back to sane defaults."""
    defaults = {
        "branch": "main",
        "remote": "origin",
        "push_times": ["09:00", "14:00", "21:00"],
    }
    if not CONFIG_FILE.exists():
        log("config.json not found — using defaults.")
        return defaults
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
            cfg = json.load(fh)
        # Merge with defaults so missing keys don't crash us
        for key, value in defaults.items():
            cfg.setdefault(key, value)
        return cfg
    except (json.JSONDecodeError, OSError) as exc:
        log(f"Warning: could not parse config.json ({exc}) — using defaults.")
        return defaults


def load_streak() -> list:
    """Load the streak log from streak.json (returns [] on first run)."""
    if not STREAK_FILE.exists():
        return []
    try:
        with open(STREAK_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            log("Warning: streak.json was not a list — resetting.")
            return []
        return data
    except (json.JSONDecodeError, OSError) as exc:
        log(f"Warning: could not read streak.json ({exc}) — starting fresh.")
        return []


def save_streak(entries: list) -> None:
    """Persist the streak log back to streak.json."""
    with open(STREAK_FILE, "w", encoding="utf-8") as fh:
        json.dump(entries, fh, indent=2, ensure_ascii=False)


def git(*args: str) -> str:
    """
    Run a git command inside SCRIPT_DIR and return its stdout.
    Raises RuntimeError on non-zero exit.
    """
    cmd = ["git"] + list(args)
    result = subprocess.run(
        cmd,
        cwd=str(SCRIPT_DIR),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(
            f"`git {' '.join(args)}` exited with code {result.returncode}\n{stderr}"
        )
    return result.stdout.strip()


# ===========================  MAIN  =======================================


def main() -> None:
    log("=" * 55)
    log("Auto-commit started")
    log("=" * 55)

    try:
        # ---- Config ----------------------------------------------------------
        config = load_config()
        branch = config["branch"]
        remote = config["remote"]
        log(f"Target: {remote}/{branch}")

        # ---- Pull latest (avoid push conflicts) -----------------------------
        try:
            git("pull", "--rebase", remote, branch)
            log("Pulled latest changes.")
        except RuntimeError as exc:
            # First push or network hiccup — non-fatal
            log(f"Pull skipped (may be first run): {exc}")

        # ---- Build new streak entry -----------------------------------------
        now = datetime.now()
        quote = random.choice(QUOTES)

        entry = {
            "id": int(now.timestamp() * 1000),          # ms-precision unique id
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "timestamp": now.isoformat(),
            "day_of_week": now.strftime("%A"),
            "quote": quote,
        }

        entries = load_streak()
        entries.append(entry)
        save_streak(entries)

        total = len(entries)
        today_count = sum(1 for e in entries if e.get("date") == entry["date"])

        log(f"Entry #{total} added  (push #{today_count} today)")
        log(f"Quote: {quote}")

        # ---- Commit & push ---------------------------------------------------
        git("add", "streak.json")

        commit_msg = (
            f"\U0001f525 Streak #{total}  \u2014  "
            f"{now.strftime('%Y-%m-%d %H:%M')}  \u2014  {quote}"
        )
        git("commit", "-m", commit_msg)
        log(f"Committed: {commit_msg}")

        git("push", remote, branch)
        log(f"Pushed to {remote}/{branch} successfully!")

    except Exception as exc:
        log(f"ERROR: {exc}")
        sys.exit(1)

    log("Auto-commit finished.\n")


if __name__ == "__main__":
    main()
