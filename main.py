"""
Main module - Entry point for the Screen Time Tracker application
"""
import time
import threading
import sys
from database import Database
from tracker import WindowTracker
from idle_detector import IdleDetector
from focus_score import FocusScoreCalculator
from ui_widget import ModernWidget
from ui_dashboard import ModernDashboard


class ScreenTimeTracker:
    def __init__(self, widget_mode=True):
        """
        Initialize the screen time tracker
        
        Args:
            widget_mode: If True, run as widget; if False, run full dashboard
        """
        self.database = Database()
        self.tracker = WindowTracker()
        self.idle_detector = IdleDetector(idle_threshold=60)
        self.focus_calculator = FocusScoreCalculator()
        self.running = False
        self.current_app = None
        self.widget_mode = widget_mode
        self.dashboard_window = None

    def track_loop(self):
        """
        Main tracking loop that runs continuously in the background
        Checks active window every second and updates database
        """
        print("Screen Time Tracker started...")
        print("Tracking will pause after 60 seconds of inactivity.")
        
        while self.running:
            try:
                # Check if user is idle
                if self.idle_detector.is_user_idle():
                    # User is idle, don't track
                    time.sleep(1)
                    continue

                # Get the currently active application
                active_app = self.tracker.get_current_app()

                if active_app and active_app != "Unknown":
                    # Update database with 1 second of usage
                    self.database.update_usage(active_app, seconds=1)
                    
                    # Print status (only when app changes)
                    if active_app != self.current_app:
                        print(f"Now tracking: {active_app}")
                        self.current_app = active_app

                # Wait for 1 second before next check
                time.sleep(1)

            except Exception as e:
                print(f"Error in tracking loop: {e}")
                time.sleep(1)

    def start_tracking(self):
        """Start the background tracking thread"""
        self.running = True
        tracking_thread = threading.Thread(target=self.track_loop, daemon=True)
        tracking_thread.start()

    def stop_tracking(self):
        """Stop the background tracking"""
        self.running = False
        self.database.close()

    def open_dashboard(self):
        """Open the full dashboard window"""
        if self.dashboard_window is None or not hasattr(self.dashboard_window, 'root'):
            print("Opening full dashboard...")
            self.dashboard_window = ModernDashboard(self.database, self.focus_calculator)
            
            # Run dashboard in a separate thread to avoid blocking the widget
            dashboard_thread = threading.Thread(
                target=self.dashboard_window.run, 
                daemon=False
            )
            dashboard_thread.start()

    def exit_application(self):
        """Exit the entire application"""
        print("Exiting Screen Time Tracker...")
        self.stop_tracking()
        sys.exit(0)

    def run_widget(self):
        """Run the application with widget UI"""
        # Start background tracking
        self.start_tracking()

        # Create and run widget
        widget = ModernWidget(
            self.database,
            self.focus_calculator,
            on_open_dashboard=self.open_dashboard,
            on_exit=self.exit_application
        )
        
        try:
            widget.run()
        finally:
            # Clean up when widget is closed
            self.stop_tracking()
            print("Screen Time Tracker stopped.")

    def run_dashboard(self):
        """Run the application with full dashboard UI"""
        # Start background tracking
        self.start_tracking()

        # Create and run dashboard
        dashboard = ModernDashboard(self.database, self.focus_calculator)
        
        try:
            dashboard.run()
        finally:
            # Clean up when dashboard()
            print("Screen Time Tracker stopped.")

    def run(self):
        """Run the application based on mode"""
        if self.widget_mode:
            self.run_widget()
        else:
            self.run_dashboard()


def main():
    """Main entry point"""
    # Check command line arguments
    widget_mode = True  # Default to widget mode
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--dashboard":
            widget_mode = False
        elif sys.argv[1] == "--widget":
            widget_mode = True
        elif sys.argv[1] == "--help":
            print("Screen Time Tracker")
            print("\nUsage:")
            print("  python main.py            # Run as desktop widget (default)")
            print("  python main.py --widget   # Run as desktop widget")
            print("  python main.py --dashboard # Run as full dashboard")
            print("  python main.py --help     # Show this help message")
            return
    
    mode_text = "widget" if widget_mode else "full dashboard"
    print(f"Starting Screen Time Tracker in {mode_text} mode...")
    
    app = ScreenTimeTracker(widget_mode=widget_mode)
    app.run()


if __name__ == "__main__":
    main()
