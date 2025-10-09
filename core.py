# core.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, date
import json
import uuid
from typing import List, Dict, Any

# ---- storage setup ----
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DATA_DIR / "tasks.json"

DATE_FMT = "%Y-%m-%d"  # e.g., 2025-10-14

@dataclass
class Task:
    id: str
    title: str
    due: str          # stored as YYYY-MM-DD
    status: str       # "Open" or "Done"

def _load_db() -> List[Task]:
    if not DB_FILE.exists():
        return []
    try:
        raw = json.loads(DB_FILE.read_text(encoding="utf-8"))
        return [Task(**t) for t in raw]
    except Exception:
        # If file is corrupted, start clean (or you could raise)
        return []

def _save_db(tasks: List[Task]) -> None:
    DB_FILE.write_text(json.dumps([asdict(t) for t in tasks], indent=2), encoding="utf-8")

def _parse_due(due_str: str) -> date:
    # Accept YYYY-MM-DD only (keep it simple)
    return datetime.strptime(due_str, DATE_FMT).date()

def _gen_id() -> str:
    return uuid.uuid4().hex[:8]

# ---------- commands ----------
def add_task(title: str, due: str) -> Task:
    _ = _parse_due(due)  # validate format
    tasks = _load_db()
    new = Task(id=_gen_id(), title=title, due=due, status="Open")
    tasks.append(new)
    _save_db(tasks)
    return new

def list_tasks() -> List[Task]:
    return _load_db()

def plan_tasks() -> List[Task]:
    # Sorted by due date; show Open first, then Done
    tasks = _load_db()
    def sort_key(t: Task):
        # Open (0) before Done (1), then by due date
        return (0 if t.status == "Open" else 1, _parse_due(t.due), t.title.lower())
    return sorted(tasks, key=sort_key)

def mark_done(prefix: str) -> Task | None:
    tasks = _load_db()
    match = _match_by_prefix(tasks, prefix)
    if not match:
        return None
    match.status = "Done"
    _save_db(tasks)
    return match

def delete_task(prefix: str) -> bool:
    tasks = _load_db()
    match = _match_by_prefix(tasks, prefix)
    if not match:
        return False
    new_tasks = [t for t in tasks if t.id != match.id]
    _save_db(new_tasks)
    return True

def _match_by_prefix(tasks: List[Task], prefix: str) -> Task | None:
    prefix = prefix.strip().lower()
    cands = [t for t in tasks if t.id.lower().startswith(prefix)]
    if len(cands) == 1:
        return cands[0]
    # If multiple or none, return None (you can enhance to handle ambiguity)
    return None

# ---- pretty printing helpers ----
def format_table(tasks: List[Task]) -> str:
    if not tasks:
        return "No tasks.\n"
    rows = [(t.id, t.title, t.due, t.status) for t in tasks]
    # column widths
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
