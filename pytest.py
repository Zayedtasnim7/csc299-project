import os
import sys
import importlib
import tempfile
import shutil
from datetime import date, timedelta


def fresh_core(tmpdir):
    """
    Create a fresh core module with isolated temp data directory.
    This prevents test data from interfering with each other.
    """
    os.environ["PKMS_DATA_DIR"] = str(tmpdir)
    # Force removal of core module to ensure fresh import
    if "core" in sys.modules:
        del sys.modules["core"]
    # Re-import core module fresh
    if "importlib" not in dir():
        import importlib
    import core as core_module
    importlib.reload(core_module)
    return core_module


def test_add_list_plan_done_delete():
    """Test basic CRUD: add, list, plan, mark done, delete."""
    tmp = tempfile.mkdtemp()
    try:
        core = fresh_core(tmp)
        
        # Add two tasks
        t1 = core.add_task("Task A", "today")
        t2 = core.add_task("Task B", "+1d")
        
        # List should have both
        lst = core.list_tasks()
        assert len(lst) == 2, f"Expected 2 tasks, got {len(lst)}"
        
        # Plan should sort Open first, then by due date
        plan = core.plan_tasks()
        assert len(plan) == 2
        assert plan[0].status == "Open", f"First task should be Open, got {plan[0].status}"
        assert plan[0].id == t1.id, f"First task should be t1, got {plan[0].id}"
        
        # Mark t1 as done
        core.mark_done(t1.id[:4])
        plan2 = core.plan_tasks()
        
        # Now t2 (Open) should come first, then t1 (Done)
        assert plan2[0].id == t2.id, f"After marking done, t2 should be first, got {plan2[0].id}"
        assert plan2[0].status == "Open", f"t2 should be Open, got {plan2[0].status}"
        assert plan2[1].status == "Done", f"t1 should be Done, got {plan2[1].status}"
        
        # Delete t1
        ok = core.delete_task(t1.id[:4])
        assert ok, "Delete should return True"
        
        # Only t2 should remain
        remaining = core.list_tasks()
        assert len(remaining) == 1, f"Expected 1 task after delete, got {len(remaining)}"
        assert remaining[0].id == t2.id, f"Remaining task should be t2"
        
    finally:
        shutil.rmtree(tmp)


def test_search_and_filters():
    """Test search, tasks_today, and tasks_overdue filters."""
    tmp = tempfile.mkdtemp()
    try:
        core = fresh_core(tmp)
        
        today = date.today()
        yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Verify we start with empty DB
        all_tasks = core.list_tasks()
        assert len(all_tasks) == 0, f"Test DB should start empty, but has {len(all_tasks)} tasks: {[t.title for t in all_tasks]}"
        
        # Add tasks with different dates
        core.add_task("Study Python", "today")
        core.add_task("Review notes", yesterday)  # overdue
        core.add_task("Complete homework", "+3d")
        
        # Search: "study" appears only in first task
        search_result = core.search_tasks("study")
        titles = [t.title for t in search_result]
        assert len(search_result) == 1, f"Expected 1 task with 'study', got {len(search_result)}. Tasks: {titles}"
        assert "Study Python" in titles
        
        # Search: "homework" appears only in third task
        search_result = core.search_tasks("homework")
        titles = [t.title for t in search_result]
        assert len(search_result) == 1, f"Expected 1 task with 'homework', got {len(search_result)}. Tasks: {titles}"
        assert "Complete homework" in titles
        
        # Tasks today
        today_tasks = core.tasks_today()
        assert len(today_tasks) == 1, f"Expected 1 task today, got {len(today_tasks)}"
        assert today_tasks[0].title == "Study Python"
        
        # Tasks overdue (only "Review notes" is past due and Open)
        overdue = core.tasks_overdue()
        assert len(overdue) == 1, f"Expected 1 overdue task, got {len(overdue)}"
        assert overdue[0].title == "Review notes"
        
    finally:
        shutil.rmtree(tmp)


def test_duplicate_guard():
    """Test that adding a duplicate task returns the existing task."""
    tmp = tempfile.mkdtemp()
    try:
        core = fresh_core(tmp)
        
        # Add a task
        t1 = core.add_task("Learn Python", "today")
        task_id_1 = t1.id
        
        # Add same task again
        t2 = core.add_task("Learn Python", "today")
        task_id_2 = t2.id
        
        # Should return the same task (same ID)
        assert task_id_1 == task_id_2, "Duplicate task should return existing task with same ID"
        
        # Only one task should exist
        lst = core.list_tasks()
        assert len(lst) == 1, f"Expected 1 task (no duplicates), got {len(lst)}"
        
    finally:
        shutil.rmtree(tmp)


def test_friendly_date_parsing():
    """Test various friendly date formats."""
    tmp = tempfile.mkdtemp()
    try:
        core = fresh_core(tmp)
        
        today = date.today()
        
        # Test "today"
        t_today = core.add_task("Due today", "today")
        assert t_today.due == today.strftime("%Y-%m-%d")
        
        # Test "tomorrow"
        t_tomorrow = core.add_task("Due tomorrow", "tomorrow")
        tomorrow = today + timedelta(days=1)
        assert t_tomorrow.due == tomorrow.strftime("%Y-%m-%d")
        
        # Test "+3d" (in 3 days)
        t_3d = core.add_task("Due in 3 days", "+3d")
        in_3d = today + timedelta(days=3)
        assert t_3d.due == in_3d.strftime("%Y-%m-%d")
        
        # Test "+2w" (in 2 weeks)
        t_2w = core.add_task("Due in 2 weeks", "+2w")
        in_2w = today + timedelta(days=14)
        assert t_2w.due == in_2w.strftime("%Y-%m-%d")
        
        # Test explicit YYYY-MM-DD
        explicit_date = "2025-12-25"
        t_explicit = core.add_task("Christmas task", explicit_date)
        assert t_explicit.due == explicit_date
        
    finally:
        shutil.rmtree(tmp)


def test_edit_task():
    """Test editing task title and due date."""
    tmp = tempfile.mkdtemp()
    try:
        core = fresh_core(tmp)
        
        # Add a task
        t = core.add_task("Original Title", "today")
        task_id = t.id[:4]
        
        # Edit title
        edited = core.edit_task(task_id, title="New Title")
        assert edited is not None
        assert edited.title == "New Title"
        
        # Edit due date
        tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        edited = core.edit_task(task_id, due="tomorrow")
        assert edited.due == tomorrow
        
        # Verify changes persisted
        tasks = core.list_tasks()
        assert tasks[0].title == "New Title"
        assert tasks[0].due == tomorrow
        
    finally:
        shutil.rmtree(tmp)


def test_plan_sections():
    """Test the plan_sections grouping functionality."""
    tmp = tempfile.mkdtemp()
    try:
        core = fresh_core(tmp)
        
        today = date.today()
        yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        next_week = (today + timedelta(days=5)).strftime("%Y-%m-%d")
        
        # Add tasks in different time buckets
        core.add_task("Overdue task", yesterday)
        core.add_task("Today task", "today")
        core.add_task("Tomorrow task", tomorrow)
        core.add_task("Next week task", next_week)
        
        # Get all tasks and group them
        tasks = core.list_tasks()
        grouped = core.plan_sections(tasks)
        
        # Verify grouping
        assert len(grouped["overdue"]) == 1
        assert len(grouped["today"]) == 1
        assert len(grouped["tomorrow"]) == 1
        assert len(grouped["upcoming"]) == 1
        
        # Verify correct tasks in each group
        assert grouped["overdue"][0].title == "Overdue task"
        assert grouped["today"][0].title == "Today task"
        assert grouped["tomorrow"][0].title == "Tomorrow task"
        assert grouped["upcoming"][0].title == "Next week task"
        
    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    print("Running tests...")
    print("-" * 50)
    
    tests = [
        ("test_add_list_plan_done_delete", test_add_list_plan_done_delete),
        ("test_search_and_filters", test_search_and_filters),
        ("test_duplicate_guard", test_duplicate_guard),
        ("test_friendly_date_parsing", test_friendly_date_parsing),
        ("test_edit_task", test_edit_task),
        ("test_plan_sections", test_plan_sections),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✓ {test_name} passed")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_name} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_name} error: {e}")
            failed += 1
    
    print("-" * 50)
    print(f"\nResults: {passed} passed, {failed} failed")
    if failed == 0:
        print("🎉 All tests passed!")
    sys.exit(0 if failed == 0 else 1)