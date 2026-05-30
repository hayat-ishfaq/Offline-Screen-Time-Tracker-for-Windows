"""
Tracker module for detecting active window on Windows
"""
import win32gui
import win32process
import psutil


class WindowTracker:
    def __init__(self):
        """Initialize window tracker"""
        self.current_app = None

    def get_active_window_process(self):
        """
        Get the process name of the currently active window
        
        Returns:
            String with process name (e.g., 'chrome.exe') or None if error
        """
        try:
            # Get the foreground window handle
            window = win32gui.GetForegroundWindow()
            
            # Get the process ID from the window handle
            _, pid = win32process.GetWindowThreadProcessId(window)
            
            # Get the process name using psutil
            process = psutil.Process(pid)
            process_name = process.name()
            
            return process_name
        except Exception as e:
            # Return None if there's an error (e.g., no active window)
            return None

    def get_current_app(self):
        """
        Get the current active application name
        
        Returns:
            String with application name or "Unknown"
        """
        app = self.get_active_window_process()
        if app:
            self.current_app = app
            return app
        return "Unknown"
