"""
AI Agent for PKMS Task Manager
Provides intelligent suggestions, reminders, and automation
"""

import core
import notes
from datetime import date, datetime, timedelta
from typing import List, Dict, Tuple
import random

# ============ AGENT INTELLIGENCE ============

def get_daily_summary() -> Dict[str, any]:
    """Generate a daily summary of tasks and priorities"""
    tasks = core.list_tasks()
    today = date.today()
    
    summary = {
        "total_tasks": len(tasks),
        "open_tasks": len([t for t in tasks if t.status == "Open"]),
        "done_tasks": len([t for t in tasks if t.status == "Done"]),
        "overdue": [],
        "today": [],
        "upcoming": [],
        "completion_rate": 0
    }
    
    # Calculate completion rate
    if summary["total_tasks"] > 0:
        summary["completion_rate"] = int((summary["done_tasks"] / summary["total_tasks"]) * 100)
    
    # Categorize tasks
    for task in tasks:
        if task.status == "Done":
            continue
            
        try:
            due_date = datetime.strptime(task.due, "%Y-%m-%d").date()
            
            if due_date < today:
                summary["overdue"].append(task)
            elif due_date == today:
                summary["today"].append(task)
            elif due_date <= today + timedelta(days=3):
                summary["upcoming"].append(task)
        except:
            pass
    
    return summary

def suggest_next_task() -> Tuple[str, str]:
    """AI suggests what task to work on next"""
    tasks = core.list_tasks()
    open_tasks = [t for t in tasks if t.status == "Open"]
    
    if not open_tasks:
        return None, "🎉 No open tasks! You're all caught up!"
    
    today = date.today()
    
    # Priority 1: Overdue tasks
    overdue = []
    for task in open_tasks:
        try:
            due_date = datetime.strptime(task.due, "%Y-%m-%d").date()
            if due_date < today:
                overdue.append((task, (today - due_date).days))
        except:
            pass
    
    if overdue:
        # Sort by how overdue (most overdue first)
        overdue.sort(key=lambda x: x[1], reverse=True)
        task, days = overdue[0]
        return task, f"⚠️  This task is {days} day(s) overdue! Start with this one."
    
    # Priority 2: Today's tasks
    today_tasks = []
    for task in open_tasks:
        try:
            due_date = datetime.strptime(task.due, "%Y-%m-%d").date()
            if due_date == today:
                today_tasks.append(task)
        except:
            pass
    
    if today_tasks:
        return today_tasks[0], "📌 This is due today. Focus on it now!"
    
    # Priority 3: Upcoming soon
    upcoming = []
    for task in open_tasks:
        try:
            due_date = datetime.strptime(task.due, "%Y-%m-%d").date()
            days_until = (due_date - today).days
            if 0 < days_until <= 3:
                upcoming.append((task, days_until))
        except:
            pass
    
    if upcoming:
        upcoming.sort(key=lambda x: x[1])
        task, days = upcoming[0]
        return task, f"⏰ Due in {days} day(s). Better start working on it!"
    
    # Default: First open task
    return open_tasks[0], "🎯 Start with this task to make progress!"

def auto_categorize_task(title: str) -> List[str]:
    """Automatically suggest categories/tags based on task title"""
    title_lower = title.lower()
    
    categories = []
    
    # Academic keywords
    if any(word in title_lower for word in ["study", "exam", "homework", "assignment", "midterm", "final", "quiz", "lecture", "class", "course"]):
        categories.append("academic")
    
    # Work keywords
    if any(word in title_lower for word in ["work", "meeting", "deadline", "project", "report", "presentation", "email"]):
        categories.append("work")
    
    # Personal keywords
    if any(word in title_lower for word in ["gym", "exercise", "workout", "clean", "laundry", "grocery", "cook", "meal"]):
        categories.append("personal")
    
    # Health keywords
    if any(word in title_lower for word in ["doctor", "appointment", "medicine", "health", "dentist"]):
        categories.append("health")
    
    # Urgent keywords
    if any(word in title_lower for word in ["urgent", "asap", "important", "critical", "emergency"]):
        categories.append("urgent")
    
    # Programming keywords
    if any(word in title_lower for word in ["code", "program", "debug", "python", "javascript", "react", "api", "database"]):
        categories.append("programming")
    
    return categories if categories else ["general"]

def get_productivity_insights() -> List[str]:
    """Provide productivity insights based on task patterns"""
    tasks = core.list_tasks()
    insights = []
    
    # Check overdue tasks
    overdue_count = len(core.tasks_overdue())
    if overdue_count > 5:
        insights.append(f"⚠️  You have {overdue_count} overdue tasks. Consider reviewing your priorities.")
    elif overdue_count > 0:
        insights.append(f"📌 {overdue_count} task(s) overdue. Try to catch up today!")
    
    # Check completion rate
    done_tasks = [t for t in tasks if t.status == "Done"]
    if len(tasks) > 0:
        completion_rate = (len(done_tasks) / len(tasks)) * 100
        if completion_rate >= 80:
            insights.append(f"🌟 Excellent! {int(completion_rate)}% completion rate!")
        elif completion_rate >= 50:
            insights.append(f"💪 Good progress! {int(completion_rate)}% tasks completed.")
        else:
            insights.append(f"🎯 {int(completion_rate)}% done. Keep pushing!")
    
    # Check today's tasks
    today_tasks = core.tasks_today()
    if len(today_tasks) > 10:
        insights.append("📅 You have many tasks today. Consider prioritizing the most important ones.")
    elif len(today_tasks) > 0:
        insights.append(f"📋 {len(today_tasks)} task(s) due today. You've got this!")
    
    # Motivational messages
    motivational = [
        "💡 Pro tip: Break large tasks into smaller, manageable chunks!",
        "⚡ Energy tip: Take short breaks between tasks to stay focused.",
        "🎯 Focus tip: Work on one task at a time for better results.",
        "📝 Organization tip: Review your tasks every morning.",
        "🌟 Remember: Progress, not perfection!",
    ]
    
    if len(insights) < 3:
        insights.append(random.choice(motivational))
    
    return insights

def suggest_task_links() -> List[Tuple[str, str, str]]:
    """Suggest which notes might be relevant to which tasks"""
    tasks = core.list_tasks()
    all_notes = notes.list_notes()
    
    suggestions = []
    
    for task in tasks:
        if task.status == "Done":
            continue
            
        task_words = set(task.title.lower().split())
        
        for note in all_notes:
            note_words = set(note.title.lower().split())
            
            # Find common words
            common = task_words & note_words
            
            if len(common) >= 1:  # At least one word in common
                suggestions.append((
                    task.id,
                    note.id,
                    f"Task '{task.title}' ↔ Note '{note.title}'"
                ))
    
    return suggestions[:5]  # Return top 5 suggestions

def check_deadline_conflicts() -> List[str]:
    """Check for potential deadline conflicts (multiple tasks due same day)"""
    tasks = core.list_tasks()
    open_tasks = [t for t in tasks if t.status == "Open"]
    
    # Group by due date
    by_date = {}
    for task in open_tasks:
        due = task.due
        if due not in by_date:
            by_date[due] = []
        by_date[due].append(task)
    
    conflicts = []
    for due_date, task_list in by_date.items():
        if len(task_list) > 3:
            conflicts.append(f"⚠️  {len(task_list)} tasks due on {due_date}. Consider rescheduling some.")
    
    return conflicts

def generate_study_plan() -> Dict[str, List]:
    """Generate a suggested study/work plan for the next few days"""
    tasks = core.list_tasks()
    open_tasks = [t for t in tasks if t.status == "Open"]
    
    today = date.today()
    plan = {
        "today": [],
        "tomorrow": [],
        "this_week": []
    }
    
    for task in open_tasks:
        try:
            due_date = datetime.strptime(task.due, "%Y-%m-%d").date()
            days_until = (due_date - today).days
            
            if days_until < 0:
                plan["today"].append(task)  # Overdue = do today
            elif days_until == 0:
                plan["today"].append(task)
            elif days_until == 1:
                plan["tomorrow"].append(task)
            elif days_until <= 7:
                plan["this_week"].append(task)
        except:
            pass
    
    return plan

def get_motivational_message() -> str:
    """Return a motivational message based on current progress"""
    summary = get_daily_summary()
    
    messages = {
        "high_completion": [
            "🌟 Amazing work! You're crushing it!",
            "🔥 You're on fire! Keep up the great work!",
            "💪 Fantastic progress! You're doing great!",
        ],
        "medium_completion": [
            "📈 Good progress! Keep going!",
            "💪 You're making steady progress. Stay focused!",
            "🎯 Doing well! A little more effort and you'll be there!",
        ],
        "low_completion": [
            "🌱 Every journey starts with a single step. You can do this!",
            "💪 Don't give up! Small progress is still progress!",
            "🎯 Focus on one task at a time. You've got this!",
        ],
        "no_tasks": [
            "✨ All clear! Time to relax or plan ahead!",
            "🎉 You're all caught up! Great job!",
            "☕ Take a well-deserved break!",
        ]
    }
    
    if summary["total_tasks"] == 0:
        return random.choice(messages["no_tasks"])
    elif summary["completion_rate"] >= 75:
        return random.choice(messages["high_completion"])
    elif summary["completion_rate"] >= 40:
        return random.choice(messages["medium_completion"])
    else:
        return random.choice(messages["low_completion"])
    
    