from tasks3.core import add_task, list_tasks, search_tasks
import os

def test_add_task():
    """Test adding a task"""
    # Clean setup
    if os.path.exists('data/tasks.json'):
        os.remove('data/tasks.json')
    
    # Add a task
    add_task("Test task", "2025-12-01")
    
    # Check it was added
    tasks = list_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "Test task"

def test_search_tasks():
    """Test searching tasks"""
    # Add some tasks first
    add_task("Python homework", "2025-12-01")
    add_task("Java assignment", "2025-12-02")
    
    # Search for Python
    results = search_tasks("Python")
    assert len(results) >= 1
    assert "Python" in results[0].title
