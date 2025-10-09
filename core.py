# core.py

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, date
from csv import DictWriter
from typing import List, Dict, Optional
import json
import uuid

# =========================
# Storage / constants
# =========================
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DATA_DIR / "tasks.json"

DATE_FMT = "%Y-%m-%d"  # e.g., 2025-10-14


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
    """Parse YYYY-MM-DD into a date (raises ValueError if bad format)."""
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


# =========================
# Commands
# =========================
def add_task(title: str, due: str) -> Task:
    """Add a task. Validates due format (YYYY-MM-DD)."""
    _ = _parse_due(due)  # validate format
    tasks = _load_db()
    new = Task(id=_gen_id(), title=title, due=due, status="Open")
    tasks.append(new)
    _save_db(tasks)
    return new

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


# =========================
# Presentation helpers
# =========================
def format_table(tasks: List[Task]) -> str:
    """Render tasks as a simple fixed-width table."""
    if not tasks:
        return "No tasks.\n"
    rows = [(t.id, t.title, t.due, t.status) for t in tasks]
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
