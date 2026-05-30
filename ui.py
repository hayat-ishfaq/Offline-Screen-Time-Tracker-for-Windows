"""
UI module for displaying screen time dashboard using Tkinter
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from focus_score import FocusScoreCalculator


class ScreenTimeUI:
    def __init__(self, database):
        """
        Initialize the UI
        
        Args:
            database: Database instance for fetching usage data
        """
        self.database = database
        self.focus_calculator = FocusScoreCalculator()
        self.root = tk.Tk()
        self.root.title("Screen Time Tracker - Dashboard")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface components"""
        # Configure root background with modern color
        self.root.configure(bg="#f1f5f9")
        
        # Header frame with modern gradient
        header_frame = tk.Frame(self.root, bg="#1e293b", pady=25)
        header_frame.pack(fill=tk.X)
        
        # Title with icon
        title_container = tk.Frame(header_frame, bg="#1e293b")
        title_container.pack()
        
        title_icon = tk.Label(
            title_container,
            text="📊",
            font=("Segoe UI", 28),
            bg="#1e293b"
        )
        title_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        title_text_frame = tk.Frame(title_container, bg="#1e293b")
        title_text_frame.pack(side=tk.LEFT)
        
        title_label = tk.Label(
            title_text_frame,
            text="Screen Time Dashboard",
            font=("Segoe UI", 24, "bold"),
            bg="#1e293b",
            fg="#f1f5f9"
        )
        title_label.pack(anchor="w")

        # Date label with icon
        date_container = tk.Frame(title_text_frame, bg="#1e293b")
        date_container.pack(anchor="w", pady=(2, 0))
        
        date_icon = tk.Label(
            date_container,
            text="📅",
            font=("Segoe UI", 10),
            bg="#1e293b"
        )
        date_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        date_str = datetime.now().strftime("%B %d, %Y")
        date_label = tk.Label(
            date_container,
            text=date_str,
            font=("Segoe UI", 11),
            bg="#1e293b",
            fg="#94a3b8"
        )
        date_label.pack(side=tk.LEFT)

        # Main content frame
        content_frame = tk.Frame(self.root, bg="#f1f5f9")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=35, pady=25)
        
        # Stats summary cards
        stats_frame = tk.Frame(content_frame, bg="#f1f5f9")
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.total_apps_label = self.create_stat_card(stats_frame, "Total Apps", "0", "#3b82f6", "📱")
        self.total_time_label = self.create_stat_card(stats_frame, "Total Time", "0h 0m", "#8b5cf6", "⏱️")
        self.focus_score_card_label = self.create_stat_card(stats_frame, "Focus Score", "0%", "#10b981", "⚡")

        # Frame for the treeview with shadow
        tree_outer_frame = tk.Frame(content_frame, bg="#cbd5e1", padx=2, pady=2)
        tree_outer_frame.pack(fill=tk.BOTH, expand=True)
        
        tree_container = tk.Frame(tree_outer_frame, bg="white")
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        tree_frame = tk.Frame(tree_container, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Scrollbar with custom styling
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview for displaying app usage
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Rank", "Application", "Category", "Time Spent"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=15
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.tree.yview)

        # Configure columns
        self.tree.heading("Rank", text="🏆")
        self.tree.heading("Application", text="Application")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Time Spent", text="Time Spent")
        
        self.tree.column("Rank", width=60, anchor="center")
        self.tree.column("Application", width=320, anchor="w")
        self.tree.column("Category", width=140, anchor="center")
        self.tree.column("Time Spent", width=150, anchor="center")

        # Enhanced styling
        style = ttk.Style()
        style.theme_use("default")
        
        # Configure treeview with modern styling
        style.configure("Treeview",
            background="white",
            foreground="#1e293b",
            rowheight=38,
            fieldbackground="white",
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        
        style.configure("Treeview.Heading",
            background="#475569",
            foreground="white",
            borderwidth=0,
            font=("Segoe UI", 11, "bold"),
            relief="flat"
        )
        
        style.map("Treeview",
            background=[("selected", "#3b82f6")],
            foreground=[("selected", "white")]
        )
        
        style.map("Treeview.Heading",
            background=[("active", "#334155")]
        )

        # Button frame
        button_frame = tk.Frame(self.root, bg="#f1f5f9", pady=20)
        button_frame.pack(fill=tk.X)

        # Refresh button with modern styling and icon
        refresh_button = tk.Button(
            button_frame,
            text="🔄  Refresh Data",
            command=self.refresh_data,
            font=("Segoe UI", 11, "bold"),
            bg="#3b82f6",
            fg="white",
            padx=35,
            pady=12,
            cursor="hand2",
            relief=tk.FLAT,
            borderwidth=0,
            activebackground="#2563eb",
            activeforeground="white"
        )
        refresh_button.pack()

        # Load initial data
        self.refresh_data()

    def create_stat_card(self, parent, title, value, color, icon):
        """Create a stat card widget"""
        card = tk.Frame(parent, bg="white", padx=20, pady=15, relief=tk.FLAT, bd=0)
        card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        
        # Shadow effect
        shadow = tk.Frame(parent, bg="#e2e8f0", padx=1, pady=1)
        shadow.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        shadow.pack_forget()
        card.pack_forget()
        shadow.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        card = tk.Frame(shadow, bg="white", padx=20, pady=15)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Icon
        icon_label = tk.Label(
            card,
            text=icon,
            font=("Segoe UI", 24),
            bg="white",
            fg=color
        )
        icon_label.pack()
        
        # Value
        value_label = tk.Label(
            card,
            text=value,
            font=("Segoe UI", 20, "bold"),
            bg="white",
            fg="#1e293b"
        )
        value_label.pack()
        
        # Title
        title_label = tk.Label(
            card,
            text=title,
            font=("Segoe UI", 9),
            bg="white",
            fg="#64748b"
        )
        title_label.pack()
        
        return value_label

    def format_time(self, seconds):
        """
        Format seconds into human-readable time
        
        Args:
            seconds: Total seconds
            
        Returns:
            Formatted string (e.g., "2h 15m", "45m", "30s")
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
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get today's usage from database
        usage_data = self.database.get_today_usage()
        
        # Update stat cards
        total_apps = len(usage_data)
        total_seconds = sum(seconds for _, seconds in usage_data)
        
        self.total_apps_label.config(text=str(total_apps))
        self.total_time_label.config(text=self.format_time(total_seconds))
        
        # Calculate and display focus score
        focus_data = self.focus_calculator.calculate_focus_score(usage_data)
        self.focus_score_card_label.config(text=f"{int(focus_data['score'])}%")

        # Populate the treeview
        if usage_data:
            rank_icons = ["🥇", "🥈", "🥉"]
            for idx, (app_name, total_seconds) in enumerate(usage_data, 1):
                formatted_time = self.format_time(total_seconds)
                
                # Get category
                category = self.focus_calculator.get_app_category(app_name)
                
                # Format category display with colors
                if category == "productive":
                    category_display = "✓ Productive"
                elif category == "distracting":
                    category_display = "✗ Distracting"
                else:
                    category_display = "◐ Neutral"
                
                # Clean app name
                clean_name = app_name.replace(".exe", "")
                
                # Rank display
                if idx <= 3:
                    rank_display = rank_icons[idx - 1]
                else:
                    rank_display = f"#{idx}"
                
                self.tree.insert("", tk.END, values=(
                    rank_display,
                    clean_name,
                    category_display,
                    formatted_time
                ))
        else:
            # Show message if no data
            self.tree.insert("", tk.END, values=("", "No data available yet", "Start using apps!", ""))

    def run(self):
        """Start the UI main loop"""
        self.root.mainloop()

    def update_in_background(self):
        """Update the display every 5 seconds when window is open"""
        self.refresh_data()
        self.root.after(5000, self.update_in_background)

    def start_auto_refresh(self):
        """Start automatic refresh every 5 seconds"""
        self.root.after(5000, self.update_in_background)
