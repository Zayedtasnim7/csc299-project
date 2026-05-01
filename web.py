from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import core
import uuid
from datetime import date

app = Flask(__name__)
app.secret_key = "focusflow-secret-key" 

def get_user_id():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
    return session["user_id"]
# =====================
# Helper functions
# =====================
def task_to_dict(task):
    """Convert Task object to dictionary."""
    return {
        'id': task.id,
        'title': task.title,
        'due': task.due,
        'status': task.status
    }

def format_date_display(date_str):
    """Format date for display (e.g., '2025-10-12' -> 'Oct 12, 2025')."""
    try:
        from datetime import datetime
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.strftime("%b %d, %Y")
    except:
        return date_str

def get_task_urgency(due_date_str):
    """Return urgency level for CSS styling."""
    try:
        from datetime import datetime
        due = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        today = date.today()
        if due < today:
            return "overdue"
        elif due == today:
            return "today"
        elif due == today + __import__('datetime').timedelta(days=1):
            return "tomorrow"
        else:
            return "upcoming"
    except:
        return "unknown"

# =====================
# Routes
# =====================

@app.route('/')
def index():
    """Main dashboard - show all tasks grouped by urgency."""
    user_id = get_user_id()
    tasks = core.list_tasks(user_id)

    grouped = core.plan_sections(tasks)
    
    # Format tasks with extra info for display
    sections = {
        'overdue': [{'task': task_to_dict(t), 'urgency': 'overdue'} for t in grouped.get('overdue', [])],
        'today': [{'task': task_to_dict(t), 'urgency': 'today'} for t in grouped.get('today', [])],
        'tomorrow': [{'task': task_to_dict(t), 'urgency': 'tomorrow'} for t in grouped.get('tomorrow', [])],
        'upcoming': [{'task': task_to_dict(t), 'urgency': 'upcoming'} for t in grouped.get('upcoming', [])],
    }
    
    return render_template('index.html', sections=sections)

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    """Add a new task."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        due = request.form.get('due', '').strip()

        if not title or not due:
            return render_template('add.html', error="Title and due date are required")

        try:
            user_id = get_user_id()
            task = core.add_task(user_id, title, due)
            return redirect(url_for('index'))
        except ValueError as e:
            return render_template('add.html', error=str(e))
        except Exception as e:
            return render_template('add.html', error=f"Error: {str(e)}")

    return render_template('add.html')

@app.route('/task/<task_id>')
def view_task(task_id):
    """View task details."""
    user_id = get_user_id()
    tasks = core.list_tasks(user_id)
    task = None
    for t in tasks:
        if t.id == task_id:
            task = task_to_dict(t)
            break
    
    if not task:
        return redirect(url_for('index'))
    
    task['urgency'] = get_task_urgency(task['due'])
    task['due_display'] = format_date_display(task['due'])
    
    return render_template('task.html', task=task)

@app.route('/edit/<task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    """Edit a task."""
    user_id = get_user_id()
    tasks = core.list_tasks(user_id)

    task = None
    for t in tasks:
        if t.id == task_id:
            task = task_to_dict(t)
            break

    if not task:
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        due = request.form.get('due', '').strip()

        if not title or not due:
            return render_template('edit.html', task=task, error="Title and due date are required")

        try:
            core.edit_task(user_id, task_id[:4], title=title, due=due)
            return redirect(url_for('view_task', task_id=task_id))
        except Exception as e:
            return render_template('edit.html', task=task, error=str(e))

    return render_template('edit.html', task=task)
    

@app.route('/done/<task_id>', methods=['POST'])
def mark_done(task_id):
    """Mark a task as done."""
    user_id = get_user_id()
    core.mark_done(user_id, task_id[:4])
    return redirect(request.referrer or url_for('index'))

@app.route('/delete/<task_id>', methods=['POST'])
def delete_task(task_id):
    """Delete a task."""
    user_id = get_user_id()
    core.delete_task(user_id, task_id[:4])
    return redirect(request.referrer or url_for('index'))

@app.route('/search')
def search():
    """Search tasks."""
    query = request.args.get('q', '').strip()
    results = []
    
    if query:
        user_id = get_user_id()
        tasks = core.search_tasks(user_id, query)

        results = [{'task': task_to_dict(t), 'urgency': get_task_urgency(t.due)} for t in tasks]
    
    return render_template('search.html', query=query, results=results)

@app.route('/api/tasks')
def api_tasks():
    """API endpoint - return all tasks as JSON."""
    tasks = core.list_tasks()
    return jsonify([task_to_dict(t) for t in tasks])@app.route('/api/tasks')

def api_tasks():
    """API endpoint - return all tasks as JSON."""
    user_id = get_user_id()
    tasks = core.list_tasks(user_id)
    return jsonify([task_to_dict(t) for t in tasks])

# =====================
# Run the app
# =====================

import os

if __name__ == "__main__":
    print("Starting FocusFlow Web App...")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)