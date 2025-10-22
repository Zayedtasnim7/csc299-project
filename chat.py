"""
Terminal Chat Interface for PKMS Task Manager
Interactive command-line interface for managing tasks and notes
"""

import core
import notes
import agent
import sys
from datetime import date

# ANSI color codes for prettier output
BOLD = '\033[1m'
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

def print_header():
    """Display welcome header"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}  📚 PKMS Study Planner - Chat Interface 📚{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
    print(f"{GREEN}Type 'help' to see available commands{RESET}")
    print(f"{GREEN}Type 'exit' or 'quit' to leave{RESET}\n")

def print_help():
    """Display all available commands"""
    commands = {
        "Task Management": [
            ("add <title> due <date>", "Add a new task"),
            ("list", "Show all tasks"),
            ("today", "Show today's tasks"),
            ("overdue", "Show overdue tasks"),
            ("plan", "Show tasks grouped by urgency"),
            ("done <id>", "Mark task as done"),
            ("delete <id>", "Delete a task"),
            ("search <query>", "Search tasks by title"),
            ("edit <id> title <new_title>", "Edit task title"),
            ("edit <id> due <new_date>", "Edit task due date"),
        ],
        "Note Management (PKMS)": [
            ("note create <title>", "Create a new note"),
            ("note list", "List all notes"),
            ("note view <id>", "View note content"),
            ("note edit <id>", "Edit note content"),
            ("note delete <id>", "Delete a note"),
            ("note search <query>", "Search notes"),
            ("note link <note_id> to <task_id>", "Link note to task"),
            ("note tag <id> add <tag>", "Add tag to note"),
            ("note tag <id> remove <tag>", "Remove tag from note"),
            ("note tags <tag>", "List notes by tag"),
        ],
        "AI Assistant": [
            ("agent summary", "Get daily summary and insights"),
            ("agent suggest", "Get AI suggestion for next task"),
            ("agent insights", "Get productivity insights"),
            ("agent plan", "Generate study/work plan"),
            ("agent links", "Get suggestions for note-task links"),
            ("agent motivate", "Get motivational message"),
        ],
        "General": [
            ("help", "Show this help message"),
            ("clear", "Clear the screen"),
            ("exit / quit", "Exit the application"),
        ]
    }
    
    print(f"\n{BOLD}{YELLOW}Available Commands:{RESET}\n")
    for category, cmds in commands.items():
        print(f"{BOLD}{category}:{RESET}")
        for cmd, desc in cmds:
            print(f"  {BLUE}{cmd:<30}{RESET} - {desc}")
        print()

def format_task(task):
    """Format a task for display"""
    status_color = GREEN if task.status == "Done" else YELLOW
    urgency = get_task_urgency(task.due)
    urgency_symbol = "🔴" if urgency == "overdue" else "🟡" if urgency == "today" else "🟢"
    
    return f"{urgency_symbol} [{BLUE}{task.id[:6]}{RESET}] {BOLD}{task.title}{RESET} (Due: {task.due}) [{status_color}{task.status}{RESET}]"

def get_task_urgency(due_date_str):
    """Determine task urgency"""
    try:
        from datetime import datetime
        due = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        today = date.today()
        if due < today:
            return "overdue"
        elif due == today:
            return "today"
        else:
            return "upcoming"
    except:
        return "unknown"

def parse_command(user_input):
    """Parse user input into command and arguments"""
    parts = user_input.strip().split(maxsplit=1)
    if not parts:
        return None, None
    
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    return command, args

def handle_add(args):
    """Handle add task command"""
    # Parse: add <title> due <date>
    if " due " not in args.lower():
        print(f"{RED}❌ Error: Use format 'add <title> due <date>'{RESET}")
        return
    
    parts = args.split(" due ", 1)
    title = parts[0].strip()
    due = parts[1].strip() if len(parts) > 1 else ""
    
    if not title or not due:
        print(f"{RED}❌ Error: Both title and due date are required{RESET}")
        return
    
    try:
        task = core.add_task(title, due)
        print(f"{GREEN}✅ Task added successfully!{RESET}")
        print(f"   {format_task(task)}")
    except Exception as e:
        print(f"{RED}❌ Error: {str(e)}{RESET}")

def handle_list():
    """Handle list tasks command"""
    tasks = core.list_tasks()
    if not tasks:
        print(f"{YELLOW}📝 No tasks found{RESET}")
        return
    
    print(f"\n{BOLD}All Tasks ({len(tasks)}):{RESET}\n")
    for task in tasks:
        print(f"  {format_task(task)}")
    print()

def handle_today():
    """Handle today's tasks command"""
    tasks = core.tasks_today()
    if not tasks:
        print(f"{YELLOW}📝 No tasks due today{RESET}")
        return
    
    print(f"\n{BOLD}Today's Tasks ({len(tasks)}):{RESET}\n")
    for task in tasks:
        print(f"  {format_task(task)}")
    print()

def handle_overdue():
    """Handle overdue tasks command"""
    tasks = core.tasks_overdue()
    if not tasks:
        print(f"{GREEN}✅ No overdue tasks!{RESET}")
        return
    
    print(f"\n{BOLD}{RED}Overdue Tasks ({len(tasks)}):{RESET}\n")
    for task in tasks:
        print(f"  {format_task(task)}")
    print()

def handle_plan():
    """Handle plan view command"""
    tasks = core.list_tasks()
    grouped = core.plan_sections(tasks)
    
    sections = [
        ("🔴 OVERDUE", "overdue", RED),
        ("📌 TODAY", "today", YELLOW),
        ("📅 TOMORROW", "tomorrow", BLUE),
        ("⏳ UPCOMING", "upcoming", GREEN),
    ]
    
    print(f"\n{BOLD}Task Plan:{RESET}\n")
    for title, key, color in sections:
        items = grouped.get(key, [])
        if items:
            print(f"{BOLD}{color}{title} ({len(items)}):{RESET}")
            for task in items:
                print(f"  {format_task(task)}")
            print()

def handle_done(args):
    """Handle mark task as done"""
    task_id = args.strip()
    if not task_id:
        print(f"{RED}❌ Error: Provide task ID (e.g., 'done abc123'){RESET}")
        return
    
    try:
        task = core.mark_done(task_id)
        if task:
            print(f"{GREEN}✅ Task marked as done!{RESET}")
            print(f"   {format_task(task)}")
        else:
            print(f"{RED}❌ Error: Task not found with ID '{task_id}'{RESET}")
    except Exception as e:
        print(f"{RED}❌ Error: {str(e)}{RESET}")

def handle_delete(args):
    """Handle delete task command"""
    task_id = args.strip()
    if not task_id:
        print(f"{RED}❌ Error: Provide task ID (e.g., 'delete abc123'){RESET}")
        return
    
    try:
        success = core.delete_task(task_id)
        if success:
            print(f"{GREEN}✅ Task deleted successfully!{RESET}")
        else:
            print(f"{RED}❌ Error: Task not found with ID '{task_id}'{RESET}")
    except Exception as e:
        print(f"{RED}❌ Error: {str(e)}{RESET}")

def handle_search(args):
    """Handle search tasks command"""
    query = args.strip()
    if not query:
        print(f"{RED}❌ Error: Provide search query (e.g., 'search homework'){RESET}")
        return
    
    tasks = core.search_tasks(query)
    if not tasks:
        print(f"{YELLOW}🔍 No tasks found matching '{query}'{RESET}")
        return
    
    print(f"\n{BOLD}Search Results for '{query}' ({len(tasks)}):{RESET}\n")
    for task in tasks:
        print(f"  {format_task(task)}")
    print()

def handle_edit(args):
    """Handle edit task command"""
    # Parse: edit <id> title <new_title> OR edit <id> due <new_date>
    parts = args.strip().split(maxsplit=2)
    if len(parts) < 3:
        print(f"{RED}❌ Error: Use 'edit <id> title <new_title>' or 'edit <id> due <new_date>'{RESET}")
        return
    
    task_id = parts[0]
    field = parts[1].lower()
    value = parts[2]
    
    try:
        if field == "title":
            task = core.edit_task(task_id, title=value)
        elif field == "due":
            task = core.edit_task(task_id, due=value)
        else:
            print(f"{RED}❌ Error: Can only edit 'title' or 'due'{RESET}")
            return
        
        if task:
            print(f"{GREEN}✅ Task updated successfully!{RESET}")
            print(f"   {format_task(task)}")
        else:
            print(f"{RED}❌ Error: Task not found with ID '{task_id}'{RESET}")
    except Exception as e:
        print(f"{RED}❌ Error: {str(e)}{RESET}")

def handle_note(args):
    """Handle all note commands"""
    parts = args.strip().split(maxsplit=1)
    if not parts:
        print(f"{RED}❌ Error: Use 'note <subcommand>'. Type 'help' for note commands.{RESET}")
        return
    
    subcommand = parts[0].lower()
    subargs = parts[1] if len(parts) > 1 else ""
    
    if subcommand == 'create':
        handle_note_create(subargs)
    elif subcommand == 'list':
        handle_note_list()
    elif subcommand == 'view':
        handle_note_view(subargs)
    elif subcommand == 'edit':
        handle_note_edit(subargs)
    elif subcommand == 'delete':
        handle_note_delete(subargs)
    elif subcommand == 'search':
        handle_note_search(subargs)
    elif subcommand == 'link':
        handle_note_link(subargs)
    elif subcommand == 'tag':
        handle_note_tag(subargs)
    elif subcommand == 'tags':
        handle_note_tags(subargs)
    else:
        print(f"{RED}❌ Unknown note subcommand: '{subcommand}'{RESET}")

def handle_note_create(args):
    """Create a new note"""
    title = args.strip()
    if not title:
        print(f"{RED}❌ Error: Provide note title (e.g., 'note create Python Notes'){RESET}")
        return
    
    print(f"{YELLOW}✏️  Enter note content (type 'END' on a new line to finish):{RESET}")
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
        except EOFError:
            break
    
    content = '\n'.join(lines)
    
    try:
        note = notes.create_note(title, content)
        print(f"{GREEN}✅ Note created successfully!{RESET}")
        print(f"   📝 [{BLUE}{note.id[:6]}{RESET}] {BOLD}{note.title}{RESET}")
        print(f"   Created: {note.created}")
    except Exception as e:
        print(f"{RED}❌ Error: {str(e)}{RESET}")

def handle_note_list():
    """List all notes"""
    all_notes = notes.list_notes()
    if not all_notes:
        print(f"{YELLOW}📝 No notes found{RESET}")
        return
    
    print(f"\n{BOLD}All Notes ({len(all_notes)}):{RESET}\n")
    for note in all_notes:
        tags_str = f" [{', '.join(note.tags)}]" if note.tags else ""
        links_str = f" 🔗{len(note.linked_tasks)}" if note.linked_tasks else ""
        print(f"  📝 [{BLUE}{note.id[:6]}{RESET}] {BOLD}{note.title}{RESET}{tags_str}{links_str}")
        print(f"     Modified: {note.modified}")
    print()

def handle_note_view(args):
    """View note content"""
    note_id = args.strip()
    if not note_id:
        print(f"{RED}❌ Error: Provide note ID (e.g., 'note view abc123'){RESET}")
        return
    
    try:
        note = notes.get_note(note_id)
        if not note:
            print(f"{RED}❌ Error: Note not found with ID '{note_id}'{RESET}")
            return
        
        print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
        print(f"{BOLD}📝 {note.title}{RESET}")
        print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
        print(note.content)
        print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
        print(f"ID: {note.id} | Created: {note.created} | Modified: {note.modified}")
        if note.tags:
            print(f"Tags: {', '.join(note.tags)}")
        if note.linked_tasks:
            print(f"Linked to {len(note.linked_tasks)} task(s)")
        print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
    except Exception as e:
        print(f"{RED}❌ Error: {str(e)}{RESET}")

def handle_note_edit(args):
    """Edit note content"""
    note_id = args.strip()
    if not note_id:
        print(f"{RED}❌ Error: Provide note ID (e.g., 'note edit abc123'){RESET}")
        return
    
    try:
        note = notes.get_note(note_id)
        if not note:
            print(f"{RED}❌ Error: Note not found with ID '{note_id}'{RESET}")
            return
        
        print(f"{YELLOW}Current content:{RESET}")
        print(note.content)
        print(f"\n{YELLOW}✏️  Enter new content (type 'END' on a new line to finish):{RESET}")
        
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
            except EOFError:
                break
        
        content = '\n'.join(lines)
        notes.update_note(note_id, content=content)
        print(f"{GREEN}✅ Note updated successfully!{RESET}")
    except Exception as e:
        print(f"{RED}❌ Error: {str(e)}{RESET}")

def handle_note_delete(args):
    """Delete a note"""
    note_id = args.strip()
    if not note_id:
        print(f"{RED}❌ Error: Provide note ID (e.g., 'note delete abc123'){RESET}")
        return
    
    try:
        success = notes.delete_note(note_id)
        if success:
            print(f"{GREEN}✅ Note deleted successfully!{RESET}")
        else:
            print(f"{RED}❌ Error: Note not found with ID '{note_id}'{RESET}")
    except Exception as e:
        print(f"{RED}❌ Error: {str(e)}{RESET}")

def handle_note_search(args):
    """Search notes"""
    query = args.strip()
    if not query:
        print(f"{RED}❌ Error: Provide search query (e.g., 'note search python'){RESET}")
        return
    
    try:
        results = notes.search_notes(query)
        if not results:
            print(f"{YELLOW}🔍 No notes found matching '{query}'{RESET}")
            return
        
        print(f"\n{BOLD}Search Results for '{query}' ({len(results)}):{RESET}\n")
        for note in results:
            print(f"  📝 [{BLUE}{note.id[:6]}{RESET}] {BOLD}{note.title}{RESET}")
        print()
    except Exception as e:
        print(f"{RED}❌ Error: {str(e)}{RESET}")

def handle_note_link(args):
    """Link note to task"""
    # Parse: note link <note_id> to <task_id>
    if " to " not in args.lower():
        print(f"{RED}❌ Error: Use 'note link <note_id> to <task_id>'{RESET}")
        return
    
    parts = args.split(" to ", 1)
    note_id = parts[0].strip()
    task_id = parts[1].strip() if len(parts) > 1 else ""
    
    if not note_id or not task_id:
        print(f"{RED}❌ Error: Provide both note ID and task ID{RESET}")
        return
    
    try:
        note = notes.link_note_to_task(note_id, task_id)
        if note:
            print(f"{GREEN}✅ Note linked to task successfully!{RESET}")
        else:
            print(f"{RED}❌ Error: Note not found with ID '{note_id}'{RESET}")
    except Exception as e:
        print(f"{RED}❌ Error: {str(e)}{RESET}")

def handle_note_tag(args):
    """Handle note tagging"""
    # Parse: note tag <id> add/remove <tag>
    parts = args.strip().split(maxsplit=2)
    if len(parts) < 3:
        print(f"{RED}❌ Error: Use 'note tag <id> add <tag>' or 'note tag <id> remove <tag>'{RESET}")
        return
    
    note_id = parts[0]
    action = parts[1].lower()
    tag = parts[2]
    
    try:
        if action == 'add':
            note = notes.add_tag(note_id, tag)
        elif action == 'remove':
            note = notes.remove_tag(note_id, tag)
        else:
            print(f"{RED}❌ Error: Action must be 'add' or 'remove'{RESET}")
            return
        
        if note:
            print(f"{GREEN}✅ Tag {action}ed successfully!{RESET}")
            print(f"   Tags: {', '.join(note.tags) if note.tags else 'None'}")
        else:
            print(f"{RED}❌ Error: Note not found with ID '{note_id}'{RESET}")
    except Exception as e:
        print(f"{RED}❌ Error: {str(e)}{RESET}")

def handle_note_tags(args):
    """List notes by tag"""
    tag = args.strip()
    if not tag:
        print(f"{RED}❌ Error: Provide tag name (e.g., 'note tags python'){RESET}")
        return
    
    try:
        results = notes.get_notes_by_tag(tag)
        if not results:
            print(f"{YELLOW}📝 No notes found with tag '{tag}'{RESET}")
            return
        
        print(f"\n{BOLD}Notes with tag '{tag}' ({len(results)}):{RESET}\n")
        for note in results:
            print(f"  📝 [{BLUE}{note.id[:6]}{RESET}] {BOLD}{note.title}{RESET}")
        print()
    except Exception as e:
        print(f"{RED}❌ Error: {str(e)}{RESET}")

def handle_agent(args):
    """Handle AI agent commands"""
    subcommand = args.strip().lower()
    
    if subcommand == 'summary':
        handle_agent_summary()
    elif subcommand == 'suggest':
        handle_agent_suggest()
    elif subcommand == 'insights':
        handle_agent_insights()
    elif subcommand == 'plan':
        handle_agent_plan()
    elif subcommand == 'links':
        handle_agent_links()
    elif subcommand == 'motivate':
        handle_agent_motivate()
    else:
        print(f"{RED}❌ Unknown agent command. Try: summary, suggest, insights, plan, links, motivate{RESET}")

def handle_agent_summary():
    """Show daily summary"""
    summary = agent.get_daily_summary()
    
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}📊 Daily Summary{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
    
    print(f"Total Tasks: {summary['total_tasks']}")
    print(f"  {GREEN}✓ Done: {summary['done_tasks']}{RESET}")
    print(f"  {YELLOW}○ Open: {summary['open_tasks']}{RESET}")
    print(f"  Completion Rate: {summary['completion_rate']}%\n")
    
    if summary['overdue']:
        print(f"{RED}⚠️  Overdue: {len(summary['overdue'])} task(s){RESET}")
    
    if summary['today']:
        print(f"{YELLOW}📌 Today: {len(summary['today'])} task(s){RESET}")
    
    if summary['upcoming']:
        print(f"{BLUE}📅 Upcoming (3 days): {len(summary['upcoming'])} task(s){RESET}")
    
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}\n")

def handle_agent_suggest():
    """Get AI task suggestion"""
    task, reason = agent.suggest_next_task()
    
    print(f"\n{BOLD}{BLUE}🤖 AI Recommendation:{RESET}\n")
    
    if task:
        print(f"{reason}\n")
        print(format_task(task))
    else:
        print(reason)
    
    print()

def handle_agent_insights():
    """Show productivity insights"""
    insights = agent.get_productivity_insights()
    
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}💡 Productivity Insights{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
    
    for insight in insights:
        print(f"  {insight}")
    
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}\n")

def handle_agent_plan():
    """Show AI-generated study plan"""
    plan = agent.generate_study_plan()
    
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}📅 Your Study/Work Plan{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
    
    if plan['today']:
        print(f"{BOLD}{YELLOW}📌 Today ({len(plan['today'])} tasks):{RESET}")
        for task in plan['today']:
            print(f"  {format_task(task)}")
        print()
    
    if plan['tomorrow']:
        print(f"{BOLD}{BLUE}📅 Tomorrow ({len(plan['tomorrow'])} tasks):{RESET}")
        for task in plan['tomorrow']:
            print(f"  {format_task(task)}")
        print()
    
    if plan['this_week']:
        print(f"{BOLD}{GREEN}📆 This Week ({len(plan['this_week'])} tasks):{RESET}")
        for task in plan['this_week']:
            print(f"  {format_task(task)}")
        print()
    
    if not plan['today'] and not plan['tomorrow'] and not plan['this_week']:
        print(f"{GREEN}✨ No upcoming tasks! You're all clear!{RESET}\n")
    
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def handle_agent_links():
    """Show note-task link suggestions"""
    suggestions = agent.suggest_task_links()
    
    print(f"\n{BOLD}{BLUE}🔗 Suggested Links:{RESET}\n")
    
    if not suggestions:
        print(f"{YELLOW}No link suggestions at the moment.{RESET}\n")
        return
    
    for i, (task_id, note_id, description) in enumerate(suggestions, 1):
        print(f"{i}. {description}")
        print(f"   Use: note link {note_id} to {task_id}\n")

def handle_agent_motivate():
    """Show motivational message"""
    message = agent.get_motivational_message()
    
    print(f"\n{BOLD}{GREEN}{'='*60}{RESET}")
    print(f"{BOLD}{message}{RESET}")
    print(f"{BOLD}{GREEN}{'='*60}{RESET}\n")

def main():
    """Main chat loop"""
    print_header()
    
    while True:
        try:
            # Prompt
            user_input = input(f"{BOLD}{BLUE}> {RESET}").strip()
            
            if not user_input:
                continue
            
            # Parse command
            command, args = parse_command(user_input)
            
            # Handle commands
            if command in ['exit', 'quit']:
                print(f"\n{GREEN}👋 Goodbye! Stay focused, stay strong! ❤️{RESET}\n")
                break
            
            elif command == 'help':
                print_help()
            
            elif command == 'clear':
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
                print_header()
            
            elif command == 'add':
                handle_add(args)
            
            elif command == 'list':
                handle_list()
            
            elif command == 'today':
                handle_today()
            
            elif command == 'overdue':
                handle_overdue()
            
            elif command == 'plan':
                handle_plan()
            
            elif command == 'done':
                handle_done(args)
            
            elif command == 'delete':
                handle_delete(args)
            
            elif command == 'search':
                handle_search(args)
            
            elif command == 'edit':
                handle_edit(args)
            
            elif command == 'note':
                handle_note(args)
            
            elif command == 'agent':
                handle_agent(args)
            
            else:
                print(f"{RED}❌ Unknown command: '{command}'. Type 'help' for available commands.{RESET}")
        
        except KeyboardInterrupt:
            print(f"\n\n{GREEN}👋 Goodbye! Stay focused, stay strong! ❤️{RESET}\n")
            break
        
        except Exception as e:
            print(f"{RED}❌ Error: {str(e)}{RESET}")

if __name__ == "__main__":
    main()