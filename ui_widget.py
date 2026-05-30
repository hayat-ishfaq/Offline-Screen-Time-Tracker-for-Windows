"""
Professional Widget UI module with modern design
"""
import tkinter as tk
from tkinter import Canvas
import math


class ModernWidget:
    def __init__(self, database, focus_calculator, on_open_dashboard=None, on_exit=None):
        """Initialize the modern widget"""
        self.database = database
        self.focus_calculator = focus_calculator
        self.on_open_dashboard = on_open_dashboard
        self.on_exit = on_exit
        
        # Create window
        self.root = tk.Tk()
        self.root.title("Screen Time")
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.95)
        self.root.attributes("-topmost", False)
        
        # Window size
        self.width = 280
        self.height = 380
        self.root.geometry(f"{self.width}x{self.height}")
        
        # Position at bottom-right
        self.position_window()
        
        # Dragging
        self.offset_x = 0
        self.offset_y = 0
        
        # Setup UI
        self.setup_ui()
        self.create_context_menu()
        
        # Auto-refresh
        self.start_auto_refresh()
        
    def position_window(self):
        """Position at bottom-right corner"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - self.width - 20
        y = screen_height - self.height - 60
        self.root.geometry(f"+{x}+{y}")
        
    def setup_ui(self):
        """Create modern UI"""
        # Main container
        main = tk.Frame(self.root, bg="#1e1e2f")
        main.pack(fill=tk.BOTH, expand=True)
        
        # Bind dragging
        main.bind("<Button-1>", self.start_drag)
        main.bind("<B1-Motion>", self.on_drag)
        main.bind("<Button-3>", self.show_context_menu)
        
        # Top accent bar
        top_bar = tk.Frame(main, bg="#4fd1c5", height=4)
        top_bar.pack(fill=tk.X)
        
        # Title section
        title_frame = tk.Frame(main, bg="#1e1e2f", pady=15)
        title_frame.pack(fill=tk.X)
        title_frame.bind("<Button-1>", self.start_drag)
        title_frame.bind("<B1-Motion>", self.on_drag)
        
        title = tk.Label(
            title_frame,
            text="TODAY'S SCREEN TIME",
            font=("Segoe UI", 10, "bold"),
            bg="#1e1e2f",
            fg="#a0a0b0"
        )
        title.pack()
        
        # Focus score section with circular progress
        score_frame = tk.Frame(main, bg="#252538", pady=20)
        score_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Circular progress canvas
        self.canvas = Canvas(
            score_frame,
            width=120,
            height=120,
            bg="#252538",
            highlightthickness=0
        )
        self.canvas.pack()
        
        self.score_text = tk.Label(
            score_frame,
            text="Focus Score",
            font=("Segoe UI", 9),
            bg="#252538",
            fg="#a0a0b0"
        )
        self.score_text.pack(pady=(5, 0))
        
        # Top apps section
        apps_header = tk.Label(
            main,
            text="TOP 5 APPS",
            font=("Segoe UI", 9, "bold"),
            bg="#1e1e2f",
            fg="#a0a0b0"
        )
        apps_header.pack(pady=(15, 5))
        
        # Apps container
        self.apps_container = tk.Frame(main, bg="#1e1e2f")
        self.apps_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        # Initial data
        self.refresh_data()
        
    def draw_circular_progress(self, score):
        """Draw circular progress meter"""
        self.canvas.delete("all")
        
        # Center and radius
        cx, cy, r = 60, 60, 50
        width = 8
        
        # Background circle
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline="#3a3a4f",
            width=width
        )
        
        # Progress arc
        if score >= 70:
            color = "#10b981"
        elif score >= 40:
            color = "#f59e0b"
        else:
            color = "#ef4444"
        
        extent = -(score / 100) * 360
        self.canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=90,
            extent=extent,
            outline=color,
            width=width,
            style=tk.ARC
        )
        
        # Center text
        self.canvas.create_text(
            cx, cy,
            text=f"{int(score)}%",
            font=("Segoe UI", 24, "bold"),
            fill=color
        )
        
    def refresh_data(self):
        """Refresh all data"""
        # Clear apps
        for widget in self.apps_container.winfo_children():
            widget.destroy()
        
        # Get data
        usage_data = self.database.get_today_usage()
        
        if not usage_data:
            # Show no data message
            no_data = tk.Label(
                self.apps_container,
                text="No data yet\nStart using apps!",
                font=("Segoe UI", 9),
                bg="#1e1e2f",
                fg="#6a6a7a",
                justify=tk.CENTER
            )
            no_data.pack(expand=True)
            
            # Set default focus score
            self.draw_circular_progress(0)
            return
        
        # Calculate focus data
        focus_data = self.focus_calculator.calculate_focus_score(usage_data)
        
        # Update focus score
        self.draw_circular_progress(focus_data['score'])
        
        # Display top 5 apps - ensure sorted by time descending
        sorted_data = sorted(usage_data, key=lambda x: x[1], reverse=True)
        top_5 = sorted_data[:5]
        
        for idx, (app_name, seconds) in enumerate(top_5):
            self.create_app_row(app_name, seconds, idx + 1)
            
    def create_app_row(self, app_name, seconds, rank):
        """Create app row"""
        row = tk.Frame(self.apps_container, bg="#252538")
        row.pack(fill=tk.X, pady=3, ipady=5, ipadx=10)
        
        # Rank
        rank_label = tk.Label(
            row,
            text=str(rank),
            font=("Segoe UI", 10, "bold"),
            bg="#252538",
            fg="#4fd1c5",
            width=2
        )
        rank_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # App name
        clean_name = app_name.replace(".exe", "").replace(".EXE", "")
        if len(clean_name) > 15:
            clean_name = clean_name[:15] + "..."
            
        category = self.focus_calculator.get_app_category(app_name)
        
        if category == "productive":
            color = "#10b981"
        elif category == "distracting":
            color = "#ef4444"
        else:
            color = "#3b82f6"
        
        name_label = tk.Label(
            row,
            text=clean_name,
            font=("Segoe UI", 9),
            bg="#252538",
            fg=color,
            anchor="w"
        )
        name_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Time
        time_label = tk.Label(
            row,
            text=self.format_time(seconds),
            font=("Segoe UI", 9, "bold"),
            bg="#252538",
            fg="#e0e0e0"
        )
        time_label.pack(side=tk.RIGHT, padx=(5, 0))
        
    def format_time(self, seconds):
        """Format time"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return f"{seconds}s"
            
    def start_drag(self, event):
        self.offset_x = event.x
        self.offset_y = event.y
        
    def on_drag(self, event):
        x = self.root.winfo_x() + event.x - self.offset_x
        y = self.root.winfo_y() + event.y - self.offset_y
        self.root.geometry(f"+{x}+{y}")
        
    def create_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0, bg="#2a2a3e", fg="white")
        self.menu.add_command(label="🔄 Refresh", command=self.refresh_data)
        self.menu.add_command(label="📊 Open Dashboard", command=self.open_dashboard)
        self.menu.add_separator()
        self.menu.add_command(label="❌ Exit", command=self.exit_app)
        
    def show_context_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()
            
    def open_dashboard(self):
        if self.on_open_dashboard:
            self.on_open_dashboard()
            
    def exit_app(self):
        if self.on_exit:
            self.on_exit()
        self.root.destroy()
        
    def start_auto_refresh(self):
        self.refresh_data()
        self.root.after(5000, self.start_auto_refresh)
        
    def run(self):
        self.root.mainloop()
