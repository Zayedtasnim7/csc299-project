# CSC299 Study Planner 📚⏰

A web-based productivity app designed to help students stay focused and manage their study tasks effectively.

![Stay Focused, Stay Strong](https://img.shields.io/badge/Stay%20Focused-Stay%20Strong-blue?style=for-the-badge)

## ✨ Features

### ⏰ Countdown Timer
- Set custom study sessions (hours and minutes)
- Visual countdown with glowing animation
- Audio alert when time's up
- Start, Pause, Resume, and Reset controls

### 📅 Interactive Calendar
- Monthly calendar view with task indicators
- Click any date to view or add tasks
- Color-coded dates (today highlighted in blue, dates with tasks in yellow)
- Navigate between months

### ✅ Task Management Board
- **To Do** column: Active tasks waiting to be completed
- **Finished** column: Completed tasks
- Click tasks to toggle between To Do ↔ Finished
- Modal popup for finished tasks with "Delete" or "Not Done Yet" options
- Add tasks quickly with simple prompts

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Zayedtasnim7/csc299-project.git
   cd csc299-project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   - Windows (PowerShell):
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install Flask**
   ```bash
   pip install flask
   ```

### Running the App

1. **Start the web server**
   ```bash
   python web.py
   ```

2. **Open your browser**
   Navigate to: `http://localhost:5000`

3. **Start studying!** 🎓

## 🎯 How to Use

### Setting Up a Study Session
1. Enter hours and minutes in the timer inputs
2. Click **Start** to begin countdown
3. Use **Pause** to take a break
4. Click **Reset** to start over

### Managing Tasks
1. Click the **+** button in the Tasks card to add a new task
2. Click any task in **To Do** to mark it as complete (moves to Finished)
3. Click a **Finished** task to open options:
   - **Not Done Yet**: Move back to To Do
   - **Delete**: Remove permanently

### Using the Calendar
1. Click any date to see tasks for that day
2. Click **+ Add Task for This Day** to create a task
3. Navigate months with ◀ ▶ arrows
4. Dates with tasks show a small orange dot

## 📁 Project Structure

```
csc299-project/
├── web.py              # Flask web server
├── core.py             # Core task management logic
├── app.py              # CLI interface (optional)
├── pytest.py           # Unit tests
├── templates/          # HTML templates
│   ├── base.html       # Base template with header
│   ├── index.html      # Main dashboard
│   ├── add.html        # Add task form
│   ├── edit.html       # Edit task form
│   ├── task.html       # Task detail view
│   └── search.html     # Search interface
├── data/               # Data storage
│   └── tasks.json      # Task database (auto-created)
├── .gitignore          # Git ignore rules
├── LICENSE             # MIT License
└── README.md           # This file
```

## 🛠️ Technology Stack

- **Backend**: Python 3, Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Data Storage**: JSON
- **Fonts**: Dancing Script (header), Poppins (timer), Inter (body)
- **Design**: Custom CSS with blue gradient theme

## ✅ Testing

Run the test suite:
```bash
python pytest.py
```

All 6 tests should pass:
- ✓ test_add_list_plan_done_delete
- ✓ test_search_and_filters
- ✓ test_duplicate_guard
- ✓ test_friendly_date_parsing
- ✓ test_edit_task
- ✓ test_plan_sections

## 🎨 Design Choices

- **Minimalist UI**: Clean, distraction-free interface
- **Calming Colors**: Soft blue background (#EAF3FF) with vibrant blue accents (#3B82F6)
- **Motivational Header**: "Stay Focused, Stay Strong ❤️" to encourage students
- **Responsive Layout**: 55/45 split for timer and tasks/calendar
- **Smooth Animations**: Glowing timer effect, modal slide-in, hover effects

## 📝 Friendly Date Formats

The app supports natural language dates:
- `today` - Today's date
- `tomorrow` - Tomorrow's date
- `+3d` - 3 days from now
- `+2w` - 2 weeks from now
- `friday` - This Friday
- `next monday` - Next Monday
- `2025-10-25` - Specific date (YYYY-MM-DD)

## 🤝 Contributing

This is a student project for CSC299. Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Zayed Tasnim**
- GitHub: [@Zayedtasnim7](https://github.com/Zayedtasnim7)

## 🎓 Course Information
-   CSC299 vibe coding      
- **Institution**: Depaul Uni
- **Semester**: Fall 2025
- **Project**: Personal Knowledge Management & Task System

## 🙏 Acknowledgments

- Built with assistance from Claude AI
- Inspired by Pomodoro Technique for time management
- Design influenced by modern productivity apps

---

**Stay Focused, Stay Strong!** ❤️ Keep studying and reach your goals! 🎯
