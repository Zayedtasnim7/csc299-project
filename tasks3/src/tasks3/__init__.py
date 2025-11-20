def inc(n: int) -> int:
    return n + 1

def main():
    """Entry point for tasks3"""
    from tasks3.core import add_task, list_tasks
    
    print("=== Tasks3 CLI ===")
    print("Adding sample tasks...")
    add_task("Complete tasks3", "2025-11-24")
    add_task("Finish tasks4", "2025-11-24")
    
    print("\nAll tasks:")
    tasks = list_tasks()
    for task in tasks:
        print(f"  - {task.title} (Due: {task.due})")

if __name__ == "__main__":
    main()
