# 🔥 Automatic GitHub Streaks Maintainer

A zero-effort automation that keeps your GitHub contribution graph green by making real commits and pushes every day — multiple times a day if you want.

## How It Works

```
Windows Task Scheduler
        │
        ▼  (runs at each scheduled time)
  auto_commit.py
        │
        ├─ Appends entry to streak.json
        ├─ git commit
        └─ git push → GitHub  ✅
```

Each run adds a timestamped entry with a random motivational quote to `streak.json`, commits it, and pushes to your GitHub repo. Your contribution graph stays green without lifting a finger.

---

## Quick Start

### 1. Create a GitHub repo

Create a **new, empty** repo on GitHub (e.g. `github-streak`). Don't use an existing project repo — this will add noise commits.

### 2. Clone it here

```bash
cd "d:\Projects\Automatic Github Streaks maintainer"
git init
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

Or if using SSH:
```bash
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
```

### 3. Configure (optional)

Edit **`config.json`** to set your preferred schedule:

```json
{
  "branch": "main",
  "remote": "origin",
  "push_times": [
    "09:00",
    "14:00",
    "21:00"
  ]
}
```

- **`push_times`** — Add as many times as you want. Each one creates a separate daily scheduled task.
- **`branch`** — The branch to push to (`main`, `master`, etc.)
- **`remote`** — Usually `origin`

### 4. Test it manually

```bash
python auto_commit.py
```

This should create `streak.json`, commit it, and push. Check your GitHub repo to confirm.

### 5. Set up the scheduler

**Run as Administrator:**

```bash
python setup.py
```

This creates Windows Scheduled Tasks for every time in `push_times`. Done! 🎉

---

## File Overview

| File | Purpose |
|---|---|
| `auto_commit.py` | Main script — updates streak.json, commits, pushes |
| `setup.py` | Creates/removes Windows Scheduled Tasks |
| `config.json` | Your settings (branch, remote, push times) |
| `streak.json` | The auto-generated streak log (committed to GitHub) |
| `run_now.bat` | Double-click to trigger a commit right now |
| `logs/` | Auto-commit logs for troubleshooting |

---

## Commands

| Command | What it does |
|---|---|
| `python auto_commit.py` | Run one commit+push cycle manually |
| `python setup.py` | Create scheduled tasks (requires Admin) |
| `python setup.py --status` | Show current scheduled tasks |
| `python setup.py --remove` | Remove all scheduled tasks |
| Double-click `run_now.bat` | Quick manual push |

---

## Customizing Push Frequency

Want 5 pushes a day? Just edit `config.json`:

```json
{
  "push_times": ["08:00", "11:00", "14:00", "17:00", "22:00"]
}
```

Then re-run `python setup.py` (as Admin) to apply.

---

## Troubleshooting

**"git push failed"**
- Make sure `git push` works manually from this directory first
- Check that your SSH key / credential manager is set up

**"Task creation failed"**
- Run `python setup.py` from an Administrator terminal

**Check logs:**
```bash
type logs\auto_commit.log
```

---

## Requirements

- **Python 3.8+**
- **Git** (with push access to your repo already configured)
- **Windows** (uses Task Scheduler)
