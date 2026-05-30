# Offline Screen Time Tracker for Windows

A Windows desktop application that tracks how much time you spend on each application. Works completely offline with local data storage.

## Features

- **Real-time tracking**: Monitors active window every second
- **Idle detection**: Pauses tracking after 60 seconds of inactivity
- **Focus Score**: Productivity scoring system based on app categories
- **App categorization**: Classify apps as productive, neutral, or distracting
- **Local storage**: Uses SQLite database for privacy
- **Desktop widget**: Minimal floating window with key metrics
- **Clean UI**: Simple Tkinter dashboard showing today's usage
- **Automatic updates**: UI refreshes every 5-10 seconds
- **Background operation**: Runs continuously while tracking

## Requirements

- Windows OS (10 or later recommended)
- Python 3.7+
- Required libraries (see requirements.txt)

## Installation

1. Install Python 3.7 or higher from [python.org](https://www.python.org/)

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Widget Mode (Default)
Run as a small desktop widget:
```bash
python main.py
```
or
```bash
python main.py --widget
```

### Full Dashboard Mode
Run with the full dashboard interface:
```bash
python main.py --dashboard
```

The application will:
1. Start tracking active windows in the background
2. Display a widget or dashboard showing today's application usage
3. Update the display automatically every 5 seconds
4. Pause tracking when you're idle for more than 60 seconds

### Widget Features
- **Always on top**: Stays visible over other windows
- **Draggable**: Click and drag to reposition anywhere on screen
- **Minimal design**: Small 250x400px borderless window
- **Focus Score**: Real-time productivity score (0-100%)
- **Category breakdown**: Shows time in productive, neutral, and distracting apps
- **Top 5 apps**: Shows your most used applications
- **Auto-refresh**: Updates every 5 seconds (apps) and 10 seconds (focus score)
- **Right-click menu**: 
  - Refresh data
  - Open full dashboard
  - Exit application

### Focus Score System

The Focus Score is a productivity metric calculated based on app usage:

**Formula:**
```focus_score.py      # Focus score calculation and app categorization
├── ui.py              # Tkinter full dashboard interface
├── widget.py          # Tkinter desktop widget interface
├── apps_config.json    # App category configurationtracting_time × 0.5) / total_time
```

**Categories:**
- **Productive** (Green): Development tools, terminals, work apps (1.0 weight)
- **Neutral** (Blue): Browsers, office apps, communication tools (0.5 weight)
- **Distracting** (Red): Games, social media, entertainment (-0.5 weight)

**Configuration:**
Edit [apps_config.json](apps_config.json) to customize app categories:
```json
{
  "Code.exe": "productive",
  "chrome.exe": "neutral",
  "Discord.exe": "distracting"
}
```

## Project Structure

```
offline_window_screnn_tracker/
├── main.py             # Entry point - starts the application
├── tracker.py          # Active window detection using Windows APIs
├── database.py         # SQLite database operations
├── idle_detector.py    # User inactivity detection
├── ui.py              # Tkinter full dashboard interface
├── widget.py          # Tkinter desktop widget interface
├── requirements.txt    # Python dependencies
├── screen_time.db     # SQLite database (created on first run)
└── README.md          # This file
```

## How It Works

1. **Window Detection**: Uses Windows APIs (`pywin32`) to detect the foreground window and extract the process name
2. **Time Tracking**: Checks active window every second and accumulates time in the database
3. **Idle Detection**: Monitors keyboard and mouse activity using Windows APIs
4. **Data Storage**: Stores daily usage in SQLite with schema: `app_usage(id, app_name, date, total_seconds)`
5. **UI Display**: Shows formatted time (e.g., "2h 15m", "45m") for each application

## Database Schema

```sql
CREATE TABLE app_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_name TEXT NOT NULL,
    date TEXT NOT NULL,
    total_seconds INTEGER DEFAULT 0,
    UNIQUE(app_name, date)
);
```

## Notes

- The application is designed for Windows only
- Data is stored locally in `screen_time.db`
- Tracking pauses automatically during inactivity
- Close the UI window to stop the application

## Troubleshooting

**Issue**: Application doesn't start
- **Solution**: Make sure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: No data is showing
- **Solution**: Use some applications and click the "Refresh" button, or wait for auto-refresh

**Issue**: Permission errors
- **Solution**: Run PowerShell or Command Prompt as Administrator

## Privacy

This application:
- Works completely offline
- Stores all data locally on your machine
- Does NOT send any data to the internet
- Does NOT capture screenshots or window content
- Only tracks application names and time spent
