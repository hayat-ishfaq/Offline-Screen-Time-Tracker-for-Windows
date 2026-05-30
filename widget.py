"""
Widget module for displaying a small desktop widget
"""
import tkinter as tk
from tkinter import font
from datetime import datetime
from focus_score import FocusScoreCalculator


class ScreenTimeWidget:
    def __init__(self, database, on_open_dashboard=None, on_exit=None):
        """
        Initialize the desktop widget
        
        Args:
            database: Database instance for fetching usage data
            on_open_dashboard: Callback function to open full dashboard
            on_exit: Callback function to exit the application
        """
        self.database = database
        self.on_open_dashboard = on_open_dashboard
        self.on_exit = on_exit
        self.focus_calculator = FocusScoreCalculator()
        
        # Create the widget window
        self.root = tk.Tk()
        self.root.title("Screen Time Widget")
        
        # Remove window decorations (title bar, borders)
        self.root.overrideredirect(True)
        
        # Don't keep widget always on top - let it stay in background
        self.root.attributes("-topmost", False)
        
        # Make window stay at bottom (behind other windows)
        self.root.attributes("-alpha", 0.95)  # Slight transparency
        self.root.lower()  # Send to back
        
        # Set window size (increased height for focus score)
        self.widget_width = 250
        self.widget_height = 400
        self.root.geometry(f"{self.widget_width}x{self.widget_height}")
        
        # Position at top-right corner
        self.position_top_right()
        
        # Make widget draggable
        self.offset_x = 0
        self.offset_y = 0
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.on_drag)
        
        # Right-click menu
        self.create_context_menu()
        self.root.bind("<Button-3>", self.show_context_menu)
        
        # Set up the UI
        self.setup_ui()
        
        # Start auto-refresh
        self.start_auto_refresh()
        self.start_focus_score_refresh()

    def position_top_right(self):
        """Position the widget at the top-right corner of the screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Position at bottom-right corner to avoid overlapping desktop icons
        x_position = screen_width - self.widget_width - 20
        y_position = screen_height - self.widget_height - 60  # Account for taskbar
        self.root.geometry(f"+{x_position}+{y_position}")

    def start_drag(self, event):
        """Record the starting position for dragging"""
        self.offset_x = event.x
        self.offset_y = event.y

    def on_drag(self, event):
        """Update widget position while dragging"""
        x = self.root.winfo_x() + event.x - self.offset_x
        y = self.root.winfo_y() + event.y - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    def create_context_menu(self):
        """Create right-click context menu"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Refresh", command=self.refresh_data)
        self.context_menu.add_command(label="Bring to Front", command=self.bring_to_front)
        self.context_menu.add_command(label="Send to Back", command=self.send_to_back)
        self.context_menu.add_command(label="Open Full Dashboard", command=self.open_dashboard)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Exit", command=self.exit_application)

    def show_context_menu(self, event):
        """Show the context menu on right-click"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def setup_ui(self):
        """Set up the widget user interface"""
        # Main container with modern gradient-like background
        self.main_frame = tk.Frame(self.root, bg="#0f172a", padx=0, pady=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top border accent
        top_accent = tk.Frame(self.main_frame, bg="#6366f1", height=3)
        top_accent.pack(fill=tk.X)
        
        # Inner padding frame
        inner_frame = tk.Frame(self.main_frame, bg="#0f172a", padx=14, pady=14)
        inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # Focus Score Section with elevated card appearance
        self.focus_frame = tk.Frame(inner_frame, bg="#1e293b", padx=12, pady=12, relief=tk.FLAT, bd=0)
        self.focus_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Add subtle shadow effect with layered frames
        shadow_frame = tk.Frame(inner_frame, bg="#334155", padx=1, pady=1)
        shadow_frame.pack(fill=tk.X, pady=(0, 12))
        shadow_frame.pack_forget()
        self.focus_frame.pack_forget()
        shadow_frame.pack(fill=tk.X, pady=(0, 12))
        self.focus_frame = tk.Frame(shadow_frame, bg="#1e293b", padx=12, pady=12)
        self.focus_frame.pack(fill=tk.BOTH)
        
        # Focus Score Title with icon
        focus_title_frame = tk.Frame(self.focus_frame, bg="#1e293b")
        focus_title_frame.pack()
        
        focus_icon = tk.Label(
            focus_title_frame,
            text="⚡",
            font=("Segoe UI", 16),
            bg="#1e293b",
            fg="#fbbf24"
        )
        focus_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        focus_title = tk.Label(
            focus_title_frame,
            text="FOCUS SCORE",
            font=("Segoe UI", 9, "bold"),
            bg="#1e293b",
            fg="#94a3b8"
        )
        focus_title.pack(side=tk.LEFT)
        
        # Focus Score Value with larger, bold display and glow effect
        self.focus_score_label = tk.Label(
            self.focus_frame,
            text="0%",
            font=("Segoe UI", 36, "bold"),
            bg="#1e293b",
            fg="#10b981"
        )
        self.focus_score_label.pack(pady=(8, 10))
        
        # Score description
        self.score_desc_label = tk.Label(
            self.focus_frame,
            text="Calculating...",
            font=("Segoe UI", 8),
            bg="#1e293b",
            fg="#64748b",
            justify=tk.CENTER
        )
        self.score_desc_label.pack(pady=(0, 8))
        
        # Category breakdown with enhanced progress bars
        self.category_frame = tk.Frame(self.focus_frame, bg="#1e293b")
        self.category_frame.pack(fill=tk.X, pady=(8, 0))
        
        # Productive category with enhanced styling
        prod_container = tk.Frame(self.category_frame, bg="#1e293b")
        prod_container.pack(fill=tk.X, pady=3)
        
        prod_label_frame = tk.Frame(prod_container, bg="#1e293b")
        prod_label_frame.pack(fill=tk.X, pady=(0, 2))
        
        self.productive_label = tk.Label(
            prod_label_frame,
            text="● Productive: 0m",
            font=("Segoe UI", 8, "bold"),
            bg="#1e293b",
            fg="#10b981",
            anchor="w"
        )
        self.productive_label.pack(side=tk.LEFT)
        
        # Rounded progress bar container
        self.productive_bar_frame = tk.Frame(prod_container, bg="#0f172a", height=6)
        self.productive_bar_frame.pack(fill=tk.X)
        self.productive_bar = tk.Frame(self.productive_bar_frame, bg="#10b981", height=6, width=0)
        self.productive_bar.place(x=0, y=0, relheight=1)
        
        # Neutral category
        neutral_container = tk.Frame(self.category_frame, bg="#1e293b")
        neutral_container.pack(fill=tk.X, pady=3)
        
        neutral_label_frame = tk.Frame(neutral_container, bg="#1e293b")
        neutral_label_frame.pack(fill=tk.X, pady=(0, 2))
        
        self.neutral_label = tk.Label(
            neutral_label_frame,
            text="● Neutral: 0m",
            font=("Segoe UI", 8, "bold"),
            bg="#1e293b",
            fg="#3b82f6",
            anchor="w"
        )
        self.neutral_label.pack(side=tk.LEFT)
        
        self.neutral_bar_frame = tk.Frame(neutral_container, bg="#0f172a", height=6)
        self.neutral_bar_frame.pack(fill=tk.X)
        self.neutral_bar = tk.Frame(self.neutral_bar_frame, bg="#3b82f6", height=6, width=0)
        self.neutral_bar.place(x=0, y=0, relheight=1)
        
        # Distracting category
        dist_container = tk.Frame(self.category_frame, bg="#1e293b")
        dist_container.pack(fill=tk.X, pady=3)
        
        dist_label_frame = tk.Frame(dist_container, bg="#1e293b")
        dist_label_frame.pack(fill=tk.X, pady=(0, 2))
        
        self.distracting_label = tk.Label(
            dist_label_frame,
            text="● Distracting: 0m",
            font=("Segoe UI", 8, "bold"),
            bg="#1e293b",
            fg="#ef4444",
            anchor="w"
        )
        self.distracting_label.pack(side=tk.LEFT)
        
        self.distracting_bar_frame = tk.Frame(dist_container, bg="#0f172a", height=6)
        self.distracting_bar_frame.pack(fill=tk.X)
        self.distracting_bar = tk.Frame(self.distracting_bar_frame, bg="#ef4444", height=6, width=0)
        self.distracting_bar.place(x=0, y=0, relheight=1)
        
        # Separator line with gradient effect
        separator = tk.Frame(inner_frame, bg="#475569", height=1)
        separator.pack(fill=tk.X, pady=10)
        
        # Title label for app list with icon
        title_frame = tk.Frame(inner_frame, bg="#0f172a")
        title_frame.pack(pady=(0, 8))
        
        title_icon = tk.Label(
            title_frame,
            text="📊",
            font=("Segoe UI", 11),
            bg="#0f172a"
        )
        title_icon.pack(side=tk.LEFT, padx=(0, 4))
        
        title_label = tk.Label(
            title_frame,
            text="TOP APPLICATIONS",
            font=("Segoe UI", 9, "bold"),
            bg="#0f172a",
            fg="#94a3b8"
        )
        title_label.pack(side=tk.LEFT)
        
        # Container for app list with card appearance
        apps_container = tk.Frame(inner_frame, bg="#1e293b", padx=10, pady=10, relief=tk.FLAT)
        apps_container.pack(fill=tk.BOTH, expand=True)
        
        self.apps_frame = tk.Frame(apps_container, bg="#1e293b")
        self.apps_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initial data load
        self.refresh_data()
        self.refresh_focus_score()

    def format_time(self, seconds):
        """
        Format seconds into human-readable time
        
        Args:
            seconds: Total seconds
            
        Returns:
            Formatted string (e.g., "2h 14m", "45m", "30s")
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60

        if hours > 0:
            if minutes > 0:
                return f"{hours}h {minutes}m"
            return f"{hours}h"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return f"{remaining_seconds}s"

    def refresh_data(self):
        """Refresh the displayed usage data"""
        # Clear existing widgets in apps_frame
        for widget in self.apps_frame.winfo_children():
            widget.destroy()
        
        # Get today's usage from database (top 5)
        all_usage = self.database.get_today_usage()
        top_5_usage = all_usage[:5] if len(all_usage) >= 5 else all_usage
        
        if top_5_usage:
            rank_colors = ["#fbbf24", "#e5e7eb", "#f97316", "#cbd5e1", "#94a3b8"]
            rank_icons = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            
            for idx, (app_name, total_seconds) in enumerate(top_5_usage):
                # Create a frame for each app entry with card-like styling
                app_frame = tk.Frame(self.apps_frame, bg="#0f172a", pady=6, padx=8, relief=tk.FLAT)
                app_frame.pack(fill=tk.X, pady=2)
                
                # Left side container
                left_container = tk.Frame(app_frame, bg="#0f172a")
                left_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Rank indicator with icon
                rank_label = tk.Label(
                    left_container,
                    text=rank_icons[idx] if idx < len(rank_icons) else "•",
                    font=("Segoe UI", 12),
                    bg="#0f172a",
                    fg=rank_colors[idx] if idx < len(rank_colors) else "#475569"
                )
                rank_label.pack(side=tk.LEFT, padx=(0, 8))
                
                # App info container
                app_info = tk.Frame(left_container, bg="#0f172a")
                app_info.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Truncate app name if too long
                display_name = app_name.replace(".exe", "")
                if len(display_name) > 15:
                    display_name = display_name[:12] + "..."
                
                # Get category color
                category = self.focus_calculator.get_app_category(app_name)
                if category == "productive":
                    category_color = "#10b981"
                    category_badge = "✓"
                elif category == "distracting":
                    category_color = "#ef4444"
                    category_badge = "✗"
                else:
                    category_color = "#3b82f6"
                    category_badge = "◐"
                
                # App name label
                app_label = tk.Label(
                    app_info,
                    text=display_name,
                    font=("Segoe UI", 9, "bold"),
                    bg="#0f172a",
                    fg="#e2e8f0",
                    anchor="w"
                )
                app_label.pack(side=tk.TOP, anchor="w")
                
                # Category badge
                category_label = tk.Label(
                    app_info,
                    text=f"{category_badge} {category.capitalize()}",
                    font=("Segoe UI", 7),
                    bg="#0f172a",
                    fg=category_color,
                    anchor="w"
                )
                category_label.pack(side=tk.TOP, anchor="w")
                
                # Time label with badge styling
                time_container = tk.Frame(app_frame, bg="#1e293b", padx=8, pady=4)
                time_container.pack(side=tk.RIGHT)
                
                time_label = tk.Label(
                    time_container,
                    text=self.format_time(total_seconds),
                    font=("Segoe UI", 9, "bold"),
                    bg="#1e293b",
                    fg="#fbbf24"
                )
                time_label.pack()
        else:
            # Show message if no data with better styling
            no_data_container = tk.Frame(self.apps_frame, bg="#1e293b", pady=20, padx=20)
            no_data_container.pack(expand=True, fill=tk.BOTH)
            
            icon_label = tk.Label(
                no_data_container,
                text="⏱️",
                font=("Segoe UI", 32),
                bg="#1e293b",
                fg="#475569"
            )
            icon_label.pack(pady=(10, 5))
            
            no_data_label = tk.Label(
                no_data_container,
                text="No data yet\n\nStart using apps\nto see tracking!",
                font=("Segoe UI", 9),
                bg="#1e293b",
                fg="#64748b",
                justify=tk.CENTER
            )
            no_data_label.pack()

    def refresh_focus_score(self):
        """Refresh the focus score display"""
        # Get all usage data
        usage_data = self.database.get_today_usage()
        
        # Calculate focus score
        focus_data = self.focus_calculator.calculate_focus_score(usage_data)
        
        # Update score label
        score = focus_data['score']
        self.focus_score_label.config(text=f"{int(score)}%")
        
        # Update color based on score with gradient
        if score >= 80:
            color = "#10b981"  # Bright green
            desc = "Excellent! 🎯"
        elif score >= 60:
            color = "#22c55e"  # Green
            desc = "Great work! 👍"
        elif score >= 40:
            color = "#f59e0b"  # Amber
            desc = "Keep going! 💪"
        elif score >= 20:
            color = "#f97316"  # Orange
            desc = "Stay focused! ⚠️"
        else:
            color = "#ef4444"  # Red
            desc = "Need improvement 🔴"
        
        self.focus_score_label.config(fg=color)
        self.score_desc_label.config(text=desc, fg=color)
        
        # Calculate progress bar widths based on total time
        total_time = focus_data['total_time']
        productive_time = focus_data['productive_time']
        neutral_time = focus_data['neutral_time']
        distracting_time = focus_data['distracting_time']
        
        max_bar_width = 100  # pixels
        
        if total_time > 0:
            prod_width = int((productive_time / total_time) * max_bar_width)
            neutral_width = int((neutral_time / total_time) * max_bar_width)
            dist_width = int((distracting_time / total_time) * max_bar_width)
        else:
            prod_width = neutral_width = dist_width = 0
        
        # Update progress bars
        self.productive_bar.config(width=prod_width)
        self.neutral_bar.config(width=neutral_width)
        self.distracting_bar.config(width=dist_width)
        
        # Update category labels
        self.productive_label.config(
            text=f"● Productive: {self.format_time(productive_time)}"
        )
        self.neutral_label.config(
            text=f"● Neutral: {self.format_time(neutral_time)}"
        )
        self.distracting_label.config(
            text=f"● Distracting: {self.format_time(distracting_time)}"
        )
    
    def start_auto_refresh(self):
        """Start automatic refresh every 5 seconds"""
        self.refresh_data()
        self.root.after(5000, self.start_auto_refresh)
    
    def start_focus_score_refresh(self):
        """Start automatic focus score refresh every 10 seconds"""
        self.refresh_focus_score()
        self.root.after(10000, self.start_focus_score_refresh)

    def open_dashboard(self):
        """Open the full dashboard"""
        if self.on_open_dashboard:
            self.on_open_dashboard()

    def bring_to_front(self):
        """Bring widget to front temporarily"""
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(100, lambda: self.root.attributes("-topmost", False))

    def send_to_back(self):
        """Send widget to back"""
        self.root.attributes("-topmost", False)
        self.root.lower()

    def exit_application(self):
        """Exit the application"""
        if self.on_exit:
            self.on_exit()
        self.root.destroy()

    def run(self):
        """Start the widget main loop"""
        self.root.mainloop()
