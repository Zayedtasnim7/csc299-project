import argparse
from typing import List, Dict

# --- Force-load local core.py by path to avoid shadowing ---
import importlib.util, pathlib, sys
_core_path = pathlib.Path(__file__).with_name("core.py")
spec = importlib.util.spec_from_file_location("core", str(_core_path))
core = importlib.util.module_from_spec(spec)
sys.modules["core"] = core
spec.loader.exec_module(core)

# --- compatibility helpers: accept dicts or dataclasses ---
from dataclasses import is_dataclass, asdict

def rowdict(x):
    """Return a plain dict for a task whether it's a dict or a dataclass/object."""
    if isinstance(x, dict):
        return x
    if is_dataclass(x):
        return asdict(x)
    # Generic object fallback
    out = {}
    for k in ("id", "title", "due", "status"):
        if hasattr(x, k):
            out[k] = getattr(x, k)
    return out

# Sanity check for expected functions (will raise early if something's missing)
for name in [
    "add_task", "edit_task", "list_tasks", "mark_done", "delete_task",
    "search_tasks", "tasks_today", "tasks_overdue", "plan_sections", "export_csv"
]:
    if not hasattr(core, name):
        raise ImportError(f"core.py is missing: {name}")

# ----------------------------
# Pretty printing helpers
# ----------------------------
def format_table(rows: List[Dict], use_color: bool = True) -> str:
    rows = [rowdict(r) for r in rows]  # normalize rows first

    if not rows:
        return "No tasks.\n"

    cols = ["id", "title", "due", "status"]
    headers = {"id": "ID", "title": "Title", "due": "Due", "status": "Status"}

    widths = {c: len(headers[c]) for c in cols}
    for r in rows:
        for c in cols:
            widths[c] = max(widths[c], len(str(r.get(c, ""))))

    def paint(text, color_code):
        if not use_color:
            return text
        return f"\033[{color_code}m{text}\033[0m"

    # header
    line = "  ".join(headers[c].ljust(widths[c]) for c in cols)
    sep  = "  ".join("-" * widths[c] for c in cols)
    out = [paint(line, "1;37"), sep]

    # body
    for r in rows:
        status = str(r.get("status", ""))
        row = "  ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols)
        # dim completed rows if colors on
        out.append(paint(row, "2") if use_color and status.lower() == "done" else row)

    return "\n".join(out) + "\n"

# ----------------------------
# Data access helpers
# ----------------------------
def _read_tasks():
    """Read tasks using core.load_tasks()."""
    return core.load_tasks()

def plan_tasks_flat() -> List[Dict]:
    """Flatten plan_sections output into a single task list with section headers."""
    grouped = core.plan_sections(_read_tasks())
    sections = [
        ("OVERDUE", "overdue"),
        ("TODAY", "today"),
        ("TOMORROW", "tomorrow"),
        ("UPCOMING (next 7d)", "upcoming"),
    ]
    rows: List[Dict] = []
    for title, key in sections:
        items = grouped.get(key, [])
        if not items:
            continue
        # Add section header row
        rows.append({"id": "--------", "title": f"[ {title} ]", "due": "", "status": ""})
        # Add tasks in this section
        rows.extend(rowdict(t) for t in items)
    return rows

# ----------------------------
# CLI
# ----------------------------
def main():
    parser = argparse.ArgumentParser(
        prog="pkms", description="Personal task manager (AI Study Planner core)"
    )
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors in output")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("-t", "--title", required=True, help="Task title")
    p_add.add_argument(
        "-d", "--due", required=True,
        help="Due date (YYYY-MM-DD or friendly: today, +3d, fri)"
    )

    # edit
    p_edit = sub.add_parser("edit", help="Edit a task title and/or due by ID prefix")
    p_edit.add_argument("id_prefix", help="ID or unique prefix")
    p_edit.add_argument("-t", "--title", help="New title")
    p_edit.add_argument("-d", "--due", help="New due (YYYY-MM-DD or friendly)")

    # list/plan/today/overdue/search
    sub.add_parser("list", help="List all tasks")
    sub.add_parser("plan", help="Plan view (grouped by urgency)")
    sub.add_parser("today", help="Tasks due today")
    sub.add_parser("overdue", help="Open tasks past due")
    p_search = sub.add_parser("search", help="Search tasks by title substring")
    p_search.add_argument("-q", "--query", required=True, help="Search text")

    # done/del/export
    p_done = sub.add_parser("done", help="Mark a task as done by ID prefix")
    p_done.add_argument("id_prefix", help="ID or unique prefix, e.g., e43a")
    p_del = sub.add_parser("del", help="Delete a task by ID prefix")
    p_del.add_argument("id_prefix", help="ID or unique prefix, e.g., e696")
    p_export = sub.add_parser("export", help="Export tasks to CSV (default: export.csv)")
    p_export.add_argument("-o", "--out", default="export.csv", help="Output CSV path")

    args = parser.parse_args()
    use_color = not args.no_color

    if args.cmd == "add":
        t = core.add_task(args.title, args.due)
        d = rowdict(t)
        print(f"Added: {d.get('id')}  {d.get('title')}  {d.get('due')}  {d.get('status')}")
        return

    elif args.cmd == "edit":
        if not args.title and not args.due:
            print("Nothing to edit. Provide --title and/or --due.")
            return
        t = core.edit_task(args.id_prefix, title=args.title, due=args.due)
        if t is None:
            print(f"No task found with ID prefix: {args.id_prefix}")
            return
        d = rowdict(t)
        print(f"Edited: {d.get('id')}  {d.get('title')}  {d.get('due')}  {d.get('status')}")
        return

    elif args.cmd == "list":
        print(format_table(core.list_tasks(), use_color=use_color), end="")
        return

    elif args.cmd == "plan":
        print(format_table(plan_tasks_flat(), use_color=use_color), end="")
        return

    elif args.cmd == "today":
        print(format_table(core.tasks_today(), use_color=use_color), end="")
        return

    elif args.cmd == "overdue":
        print(format_table(core.tasks_overdue(), use_color=use_color), end="")
        return

    elif args.cmd == "search":
        print(format_table(core.search_tasks(args.query), use_color=use_color), end="")
        return

    elif args.cmd == "done":
        t = core.mark_done(args.id_prefix)
        if t is None:
            print(f"No task found with ID prefix: {args.id_prefix}")
            return
        d = rowdict(t)
        print(f"Marked done: {d.get('id')}  {d.get('title')}")
        return

    elif args.cmd == "del":
        ok = core.delete_task(args.id_prefix)
        if ok:
            print("Deleted.")
        else:
            print(f"No task found with ID prefix: {args.id_prefix}")
        return

    elif args.cmd == "export":
        out = core.export_csv(args.out)
        print(f"Exported to {out}")
        return

if __name__ == "__main__":
    main()