from flask import Flask, render_template, request, jsonify, redirect, url_for
import core
from datetime import date

app = Flask(__name__)

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
    tasks = core.list_tasks()
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
            task = core.add_task(title, due)
            return redirect(url_for('index'))
        except ValueError as e:
            return render_template('add.html', error=str(e))
        except Exception as e:
            return render_template('add.html', error=f"Error: {str(e)}")
    
    return render_template('add.html')

@app.route('/task/<task_id>')
def view_task(task_id):
    """View task details."""
    tasks = core.list_tasks()
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
    tasks = core.list_tasks()
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
            core.edit_task(task_id[:4], title=title, due=due)
            return redirect(url_for('view_task', task_id=task_id))
        except Exception as e:
            return render_template('edit.html', task=task, error=str(e))
    
    return render_template('edit.html', task=task)

@app.route('/done/<task_id>', methods=['POST'])
def mark_done(task_id):
    """Mark a task as done."""
    core.mark_done(task_id[:4])
    return redirect(request.referrer or url_for('index'))

@app.route('/delete/<task_id>', methods=['POST'])
def delete_task(task_id):
    """Delete a task."""
    core.delete_task(task_id[:4])
    return redirect(request.referrer or url_for('index'))

@app.route('/search')
def search():
    """Search tasks."""
    query = request.args.get('q', '').strip()
    results = []
    
    if query:
        tasks = core.search_tasks(query)
        results = [{'task': task_to_dict(t), 'urgency': get_task_urgency(t.due)} for t in tasks]
    
    return render_template('search.html', query=query, results=results)

@app.route('/api/tasks')
def api_tasks():
    """API endpoint - return all tasks as JSON."""
    tasks = core.list_tasks()
    return jsonify([task_to_dict(t) for t in tasks])

# =====================
# Run the app
# =====================

if __name__ == '__main__':
    print("Starting PKMS Task Manager Web UI...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, port=5000)

    