import os
import sys
import json
import uuid
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, date, timedelta
from csv import DictWriter
from typing import List, Dict, Optional

# =========================
# Storage / constants
# =========================
DATA_DIR = Path(os.environ.get("PKMS_DATA_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DATA_DIR / "tasks.json"

DATE_FMT = "%Y-%m-%d"  # e.g., 2025-10-14

# ANSI colors (used only if allowed)
RESET = "\x1b[0m"
BOLD = "\x1b[1m"
RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"

def _should_color() -> bool:
    if os.environ.get("PKMS_NO_COLOR", "").lower() in ("1", "true", "yes"):
        return False
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


# =========================
# Data model
# =========================
@dataclass
class Task:
    id: str
    title: str
    due: str          # stored as YYYY-MM-DD
    status: str       # "Open" or "Done"


# =========================
# Internal helpers
# =========================
def _load_db() -> List[Task]:
    """Load tasks from JSON, returning an empty list if file is missing/corrupt."""
    if not DB_FILE.exists():
        return []
    try:
        raw = json.loads(DB_FILE.read_text(encoding="utf-8"))
        return [Task(**t) for t in raw]
    except Exception:
        return []

def _save_db(tasks: List[Task]) -> None:
    """Persist tasks to JSON with pretty-printing."""
    DB_FILE.write_text(json.dumps([asdict(t) for t in tasks], indent=2), encoding="utf-8")

def _parse_due(due_str: str) -> date:
    """Parse strict YYYY-MM-DD into a date."""
    return datetime.strptime(due_str, DATE_FMT).date()

def _gen_id() -> str:
    """Short, human-friendly ID."""
    return uuid.uuid4().hex[:8]

def _match_by_prefix(tasks: List[Task], prefix: str) -> Optional[Task]:
    """Return the unique task whose id starts with `prefix`, or None."""
    prefix = prefix.strip().lower()
    cands = [t for t in tasks if t.id.lower().startswith(prefix)]
    if len(cands) == 1:
        return cands[0]
    return None

def _today() -> date:
    return date.today()


# =========================
# Friendly date parsing
# =========================
_WEEKDAYS = {
    "mon": 0, "monday": 0,
    "tue": 1, "tues": 1, "tuesday": 1,
    "wed": 2, "wednesday": 2,
    "thu": 3, "thur": 3, "thurs": 3, "thursday": 3,
    "fri": 4, "friday": 4,
    "sat": 5, "saturday": 5,
    "sun": 6, "sunday": 6,
}

def _next_weekday(target_idx: int, *, include_today: bool = True, weeks_ahead: int = 0) -> date:
    today = _today()
    today_idx = today.weekday()
    ahead = (target_idx - today_idx) % 7
    if not include_today and ahead == 0:
        ahead = 7
    ahead += 7 * max(weeks_ahead, 0)
    return today + timedelta(days=ahead)

def parse_due_friendly(s: str) -> str:
    """
    Accepts:
      - 'YYYY-MM-DD'
      - 'today', 'tomorrow'
      - weekday names: 'fri', 'monday', or 'next fri'
      - relative: '+3d', '+2w'
    Returns canonical 'YYYY-MM-DD' or raises ValueError.
    """
    s0 = s.strip().lower()

    # strict YYYY-MM-DD
    try:
        return _parse_due(s0).strftime(DATE_FMT)
    except Exception:
        pass

    if s0 in ("today",):
        return _today().strftime(DATE_FMT)
    if s0 in ("tomorrow", "tmr", "tmrw"):
        return (_today() + timedelta(days=1)).strftime(DATE_FMT)

    # +Nd / +Nw
    m = re.match(r"^\+(\d+)\s*([dw])$", s0)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        delta = timedelta(days=n if unit == "d" else n * 7)
        return (_today() + delta).strftime(DATE_FMT)

    # next <weekday>
    m = re.match(r"^next\s+([a-z]+)$", s0)
    if m and m.group(1) in _WEEKDAYS:
        idx = _WEEKDAYS[m.group(1)]
        return _next_weekday(idx, include_today=False, weeks_ahead=1).strftime(DATE_FMT)

    # weekday alone
    if s0 in _WEEKDAYS:
        idx = _WEEKDAYS[s0]
        return _next_weekday(idx, include_today=True).strftime(DATE_FMT)

    raise ValueError(f"Unrecognized date: {s!r} (try YYYY-MM-DD, today, tomorrow, fri, next mon, +3d, +2w)")


# =========================
# Commands
# =========================
def add_task(title: str, due: str):
    """Add a new task unless one with the same (title, due) already exists; return the task."""
    tasks = _load_db()

    # Parse friendly date to YYYY-MM-DD format
    try:
        ndue = parse_due_friendly(due)
    except ValueError:
        ndue = due.strip()

    # Duplicate guard: return existing task with same (title, due)
    for t in tasks:
        if t.title.strip() == title.strip() and t.due == ndue:
            return t

    # Create new task
    new_task = Task(id=_gen_id(), title=title.strip(), due=ndue, status="Open")
    tasks.append(new_task)
    _save_db(tasks)
    return new_task


def edit_task(prefix: str, *, title: Optional[str] = None, due: Optional[str] = None) -> Optional[Task]:
    """Edit a task's title and/or due by ID prefix."""
    tasks = _load_db()
    t = _match_by_prefix(tasks, prefix)
    if not t:
        return None
    if title is None and due is None:
        return t
    if title is not None:
        t.title = title
    if due is not None:
        t.due = parse_due_friendly(due)
    _save_db(tasks)
    return t

def list_tasks() -> List[Task]:
    """Return tasks in stored order."""
    return _load_db()

def plan_tasks() -> List[Task]:
    """Return tasks sorted: Open first, then by due date, then by title."""
    tasks = _load_db()
    def sort_key(t: Task):
        return (0 if t.status == "Open" else 1, _parse_due(t.due), t.title.lower())
    return sorted(tasks, key=sort_key)

def mark_done(prefix: str) -> Optional[Task]:
    """Mark the task (by unique ID prefix) as Done. Returns the task or None."""
    tasks = _load_db()
    match = _match_by_prefix(tasks, prefix)
    if not match:
        return None
    match.status = "Done"
    _save_db(tasks)
    return match

def delete_task(prefix: str) -> bool:
    """Delete a task (by unique ID prefix). Returns True if deleted."""
    tasks = _load_db()
    match = _match_by_prefix(tasks, prefix)
    if not match:
        return False
    new_tasks = [t for t in tasks if t.id != match.id]
    _save_db(new_tasks)
    return True

def search_tasks(query: str) -> List[Task]:
    """Case-insensitive substring search in title."""
    q = query.strip().lower()
    return [t for t in _load_db() if q in t.title.lower()]

def tasks_today() -> List[Task]:
    """Tasks due today."""
    today_s = _today().strftime(DATE_FMT)
    return [t for t in _load_db() if t.due == today_s]

def tasks_overdue() -> List[Task]:
    """Open tasks past due date."""
    today = _today()
    out = []
    for t in _load_db():
        try:
            if t.status == "Open" and _parse_due(t.due) < today:
                out.append(t)
        except Exception:
            pass
    return out


# =========================
# Plan sections for grouped view
# =========================
def plan_sections(tasks, today: date | None = None):
    """
    Group tasks into sections for the 'plan' view.
    Expected each task to be a dict with at least: {'title', 'due', 'status', 'id'}.
    Returns a dict: {'overdue': [...], 'today': [...], 'tomorrow': [...], 'upcoming': [...]}
    """
    today = today or date.today()
    tomorrow = today + timedelta(days=1)
    week_ahead = today + timedelta(days=7)

    def parse_due(d):
        # accept date or string YYYY-MM-DD
        if isinstance(d, date):
            return d
        try:
            return datetime.strptime(d, DATE_FMT).date()
        except Exception:
            # if bad/missing date, shove into upcoming so it still shows
            return week_ahead

    buckets = {"overdue": [], "today": [], "tomorrow": [], "upcoming": []}

    for t in tasks:
        due = parse_due(t.get("due") if isinstance(t, dict) else t.due)
        status = t.get("status") if isinstance(t, dict) else t.status
        
        if due < today:
            if str(status).lower() != "done":
                buckets["overdue"].append(t)
        elif due == today:
            buckets["today"].append(t)
        elif due == tomorrow:
            buckets["tomorrow"].append(t)
        elif today < due <= week_ahead:
            buckets["upcoming"].append(t)

    # Sort each bucket by due then title for stable output
    for k in buckets:
        buckets[k].sort(key=lambda x: (parse_due(x.get("due") if isinstance(x, dict) else x.due), 
                                       str(x.get("title") if isinstance(x, dict) else x.title).lower()))
    return buckets


# =========================
# Public load/save aliases (for app.py compatibility)
# =========================
def load_tasks() -> List[Task]:
    """Public alias for _load_db()."""
    return _load_db()

def save_tasks(tasks: List[Task]) -> None:
    """Public alias for _save_db()."""
    _save_db(tasks)


# =========================
# Presentation helpers
# =========================
def _style_status(t: Task, use_color: bool) -> str:
    if not use_color:
        return t.status
    try:
        d = _parse_due(t.due)
    except Exception:
        d = None
    if t.status == "Done":
        return f"{GREEN}{t.status}{RESET}"
    if d:
        if d < _today():
            return f"{RED}{t.status}{RESET}"
        if d == _today():
            return f"{YELLOW}{t.status}{RESET}"
    return t.status

def format_table(tasks: List[Task], use_color: Optional[bool] = None) -> str:
    """Render tasks as a simple fixed-width table."""
    if use_color is None:
        use_color = _should_color()
    if not tasks:
        return "No tasks.\n"
    rows = [(t.id, t.title, t.due, _style_status(t, use_color)) for t in tasks]
    id_w = max(8, max(len(r[0]) for r in rows))
    title_w = max(9, max(len(r[1]) for r in rows))
    due_w = 10
    status_w = max(6, max(len(r[3]) for r in rows))
    header = f"{'ID':<{id_w}}  {'Title':<{title_w}}  {'Due':<{due_w}}  {'Status':<{status_w}}"
    sep = f"{'-'*id_w}  {'-'*title_w}  {'-'*due_w}  {'-'*status_w}"
    lines = [header, sep]
    for r in rows:
        lines.append(f"{r[0]:<{id_w}}  {r[1]:<{title_w}}  {r[2]:<{due_w}}  {r[3]:<{status_w}}")
    return "\n".join(lines) + "\n"


# =========================
# CSV export
# =========================
def to_rows(tasks: List[Task]) -> List[Dict[str, str]]:
    """Convert Task objects to dictionaries suitable for CSV writing."""
    return [
        {"id": t.id, "title": t.title, "due": t.due, "status": t.status}
        for t in tasks
    ]

def export_csv(path: str = "export.csv") -> str:
    """
    Export all tasks to CSV at `path` (default: export.csv).
    Returns the path written.
    """
    tasks = _load_db()
    rows = to_rows(tasks)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = DictWriter(f, fieldnames=["id", "title", "due", "status"])
        writer.writeheader()
        writer.writerows(rows)
    return path