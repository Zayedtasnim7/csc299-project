# app.py
import argparse
from core import (
    add_task,
    list_tasks,
    plan_tasks,
    mark_done,
    delete_task,
    format_table,
    export_csv,
)

def main():
    parser = argparse.ArgumentParser(
        prog="pkms",
        description="Personal task manager (AI Study Planner core)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("-t", "--title", required=True, help="Task title")
    p_add.add_argument("-d", "--due", required=True, help="Due date (YYYY-MM-DD)")

    # list
    sub.add_parser("list", help="List all tasks")

    # plan
    sub.add_parser("plan", help="Plan view (Open first, sorted by due)")

    # done
    p_done = sub.add_parser("done", help="Mark a task as done by ID prefix")
    p_done.add_argument("id_prefix", help="ID or unique prefix, e.g., e43a")

    # del
    p_del = sub.add_parser("del", help="Delete a task by ID prefix")
    p_del.add_argument("id_prefix", help="ID or unique prefix, e.g., e696")

    # export
    p_export = sub.add_parser("export", help="Export tasks to CSV (default: export.csv)")
    p_export.add_argument(
        "-o", "--out", default="export.csv", help="Output CSV path"
    )

    args = parser.parse_args()

    if args.cmd == "add":
        t = add_task(args.title, args.due)
        print(f"Added: {t.id}  {t.title}  {t.due}  {t.status}")
    elif args.cmd == "list":
        print(format_table(list_tasks()), end="")
    elif args.cmd == "plan":
        print(format_table(plan_tasks()), end="")
    elif args.cmd == "done":
        t = mark_done(args.id_prefix)
        print(f"Marked done: {t.id}  {t.title}") if t else print("No matching ID.")
    elif args.cmd == "del":
        ok = delete_task(args.id_prefix)
        print("Deleted." if ok else "No matching ID.")
    elif args.cmd == "export":
        out = export_csv(args.out)
        print(f"Exported to {out}")

if __name__ == "__main__":
    main()
