# Pomodoro Timer CLI
# A fully functional Pomodoro productivity timer in the terminal.
# Shows a live Rich progress bar countdown, tracks sessions,
# plays a terminal beep at the end of each interval, and logs sessions.
#
# Install: pip install rich
# Usage:   python pomodoro.py
#          python pomodoro.py --work 25 --short-break 5 --long-break 15

import time
import argparse
import json
import os
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TextColumn
from rich.panel import Panel

console = Console()
LOG_FILE = "pomodoro_log.json"

def load_log():
    # Load existing session log from disk, or return empty list
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return json.load(f)
    return []

def save_session(session_type, duration_min):
    # Append completed session to the JSON log file
    log = load_log()
    log.append({
        "type": session_type,
        "duration": duration_min,
        "at": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

def beep():
    # Terminal bell — simple audio cue without any extra library
    print("\a", end="", flush=True)

def run_timer(label, minutes, color):
    total_secs = minutes * 60
    console.print(Panel(f"[{color}]{label}[/{color}] — {minutes} minutes", expand=False))

    # Rich progress bar that counts down second by second
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40, complete_style=color),
        TimeRemainingColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(label, total=total_secs)
        elapsed = 0
        while elapsed < total_secs:
            time.sleep(1)
            elapsed += 1
            progress.update(task, advance=1)

    beep()
    console.print(f"[{color}]✓ {label} complete![/{color}]")
    save_session(label, minutes)

def main():
    parser = argparse.ArgumentParser(description="Pomodoro Timer")
    parser.add_argument("--work", type=int, default=25, help="Work duration in minutes")
    parser.add_argument("--short-break", type=int, default=5, help="Short break duration")
    parser.add_argument("--long-break", type=int, default=15, help="Long break after 4 sessions")
    args = parser.parse_args()

    session = 0
    console.print("[bold]Pomodoro Timer started. Press Ctrl+C to stop.[/bold]\n")

    while True:
        session += 1
        console.print(f"\n[dim]Session {session}[/dim]")
        run_timer("Work", args.work, "green")

        # Every 4th completed session earns a longer break
        if session % 4 == 0:
            run_timer("Long Break", args.long_break, "blue")
        else:
            run_timer("Short Break", args.short_break, "yellow")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log = load_log()
        work_sessions = sum(1 for s in log if s["type"] == "Work")
        console.print(f"\n[bold]Session ended. Total work sessions logged: {work_sessions}[/bold]")
