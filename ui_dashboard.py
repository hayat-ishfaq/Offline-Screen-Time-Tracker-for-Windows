"""
Professional Dashboard UI with analytics and charts
"""
import tkinter as tk
from tkinter import ttk, Canvas, filedialog, messagebox
from datetime import datetime, timedelta
import csv


class ModernDashboard:
    def __init__(self, database, focus_calculator):
        """Initialize modern dashboard"""
        self.database = database
        self.focus_calculator = focus_calculator
        
        self.root = tk.Toplevel()
        self.root.title("Screen Time Dashboard")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1e1e2f")
        self.root.resizable(True, True)
        
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Create dashboard UI"""
        # Header
        header = tk.Frame(self.root, bg="#252538", pady=20)
        header.pack(fill=tk.X)
        
        title = tk.Label(
            header,
            text="📊 SCREEN TIME ANALYTICS",
            font=("Segoe UI", 20, "bold"),
            bg="#252538",
            fg="#ffffff"
        )
        title.pack()
        
        date_str = datetime.now().strftime("%B %d, %Y")
        subtitle = tk.Label(
            header,
            text=date_str,
            font=("Segoe UI", 11),
            bg="#252538",
            fg="#a0a0b0"
        )
        subtitle.pack(pady=(5, 0))
        
        # Main content
        content = tk.Frame(self.root, bg="#1e1e2f")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Top section: Stats cards + Focus chart
        top_section = tk.Frame(content, bg="#1e1e2f")
        top_section.pack(fill=tk.X, pady=(0, 20))
        
        # Left: Stats cards
        stats_col = tk.Frame(top_section, bg="#1e1e2f")
        stats_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.total_time_card = self.create_stat_card(stats_col, "⏱️", "Total Time", "0h 0m", "#4fd1c5")
        self.productive_card = self.create_stat_card(stats_col, "✓", "Productive", "0h 0m", "#10b981")
        self.distracting_card = self.create_stat_card(stats_col, "✗", "Distracting", "0h 0m", "#ef4444")
        
        # Right: Focus score circular chart
        focus_col = tk.Frame(top_section, bg="#252538", padx=20, pady=20)
        focus_col.pack(side=tk.RIGHT, padx=(20, 0))
        
        focus_title = tk.Label(
            focus_col,
            text="FOCUS SCORE",
            font=("Segoe UI", 11, "bold"),
            bg="#252538",
            fg="#a0a0b0"
        )
        focus_title.pack()
        
        self.focus_canvas = Canvas(
            focus_col,
            width=180,
            height=180,
            bg="#252538",
            highlightthickness=0
        )
        self.focus_canvas.pack(pady=10)
        
        # Middle section: App list and bar chart
        middle_section = tk.Frame(content, bg="#1e1e2f")
        middle_section.pack(fill=tk.BOTH, expand=True)
        
        # Left: App table
        table_frame = tk.Frame(middle_section, bg="#252538", padx=2, pady=2)
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        table_label = tk.Label(
            table_frame,
            text="APPLICATION USAGE",
            font=("Segoe UI", 10, "bold"),
            bg="#252538",
            fg="#ffffff",
            pady=10
        )
        table_label.pack()
        
        # Treeview
        tree_container = tk.Frame(table_frame, bg="#252538")
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(tree_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            tree_container,
            columns=("Rank", "App", "Category", "Time"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=12
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Configure columns
        self.tree.heading("Rank", text="🏆")
        self.tree.heading("App", text="Application")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Time", text="Time")
        
        self.tree.column("Rank", width=50, anchor="center")
        self.tree.column("App", width=200, anchor="w")
        self.tree.column("Category", width=100, anchor="center")
        self.tree.column("Time", width=80, anchor="center")
        
        # Style treeview
        style = ttk.Style()
        style.configure("Treeview",
            background="#2a2a3e",
            foreground="#ffffff",
            rowheight=30,
            fieldbackground="#2a2a3e",
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure("Treeview.Heading",
            background="#3a3a4f",
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold")
        )
        style.map("Treeview",
            background=[("selected", "#4fd1c5")],
            foreground=[("selected", "#ffffff")]
        )
        
        # Right: Bar chart
        chart_frame = tk.Frame(middle_section, bg="#252538", padx=10, pady=10)
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        chart_label = tk.Label(
            chart_frame,
            text="TOP 10 APPS",
            font=("Segoe UI", 10, "bold"),
            bg="#252538",
            fg="#ffffff",
            pady=10
        )
        chart_label.pack()
        
        self.chart_canvas = Canvas(
            chart_frame,
            width=350,
            height=400,
            bg="#2a2a3e",
            highlightthickness=0
        )
        self.chart_canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Bottom: Action buttons
        button_frame = tk.Frame(self.root, bg="#1e1e2f", pady=15)
        button_frame.pack(fill=tk.X)
        
        self.create_button(button_frame, "🔄 Refresh", self.refresh_data, "#4fd1c5")
        self.create_button(button_frame, "📥 Export CSV", self.export_csv, "#3b82f6")
        self.create_button(button_frame, "🎯 Focus Session", self.start_focus_session, "#10b981")
        self.create_button(button_frame, "❌ Close", self.root.destroy, "#ef4444")
        
    def create_stat_card(self, parent, icon, title, value, color):
        """Create a stat card"""
        card = tk.Frame(parent, bg="#252538", pady=15, padx=20)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        icon_label = tk.Label(
            card,
            text=icon,
            font=("Segoe UI", 28),
            bg="#252538",
            fg=color
        )
        icon_label.pack()
        
        value_label = tk.Label(
            card,
            text=value,
            font=("Segoe UI", 18, "bold"),
            bg="#252538",
            fg="#ffffff"
        )
        value_label.pack()
        
        title_label = tk.Label(
            card,
            text=title,
            font=("Segoe UI", 9),
            bg="#252538",
            fg="#a0a0b0"
        )
        title_label.pack()
        
        return value_label
        
    def create_button(self, parent, text, command, color):
        """Create styled button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10, "bold"),
            bg=color,
            fg="#ffffff",
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            borderwidth=0
        )
        btn.pack(side=tk.LEFT, padx=10)
        
    def refresh_data(self):
        """Refresh all data and charts"""
        # Get data
        usage_data = self.database.get_today_usage()
        focus_data = self.focus_calculator.calculate_focus_score(usage_data)
        
        # Update stat cards
        total_time = focus_data['total_time']
        self.total_time_card.config(text=self.format_time(total_time))
        self.productive_card.config(text=self.format_time(focus_data['productive_time']))
        self.distracting_card.config(text=self.format_time(focus_data['distracting_time']))
        
        # Update focus chart
        self.draw_focus_chart(focus_data['score'])
        
        # Update table
        self.tree.delete(*self.tree.get_children())
        
        rank_icons = ["🥇", "🥈", "🥉"]
        for idx, (app_name, seconds) in enumerate(usage_data, 1):
            category = self.focus_calculator.get_app_category(app_name)
            
            if category == "productive":
                cat_display = "✓ Productive"
            elif category == "distracting":
                cat_display = "✗ Distracting"
            else:
                cat_display = "◐ Neutral"
            
            rank = rank_icons[idx - 1] if idx <= 3 else f"#{idx}"
            clean_name = app_name.replace(".exe", "")
            
            self.tree.insert("", tk.END, values=(
                rank,
                clean_name,
                cat_display,
                self.format_time(seconds)
            ))
        
        # Update bar chart
        self.draw_bar_chart(usage_data[:10])
        
    def draw_focus_chart(self, score):
        """Draw circular focus score chart"""
        self.focus_canvas.delete("all")
        
        cx, cy, r = 90, 90, 70
        width = 12
        
        # Background circle
        self.focus_canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline="#3a3a4f",
            width=width
        )
        
        # Determine color
        if score >= 70:
            color = "#10b981"
        elif score >= 40:
            color = "#f59e0b"
        else:
            color = "#ef4444"
        
        # Progress arc
        extent = -(score / 100) * 360
        self.focus_canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=90,
            extent=extent,
            outline=color,
            width=width,
            style=tk.ARC
        )
        
        # Center text
        self.focus_canvas.create_text(
            cx, cy - 10,
            text=f"{int(score)}%",
            font=("Segoe UI", 32, "bold"),
            fill=color
        )
        
        # Label
        if score >= 70:
            label = "Excellent!"
        elif score >= 40:
            label = "Good"
        else:
            label = "Needs Work"
            
        self.focus_canvas.create_text(
            cx, cy + 25,
            text=label,
            font=("Segoe UI", 11),
            fill="#a0a0b0"
        )
        
    def draw_bar_chart(self, data):
        """Draw horizontal bar chart for top apps"""
        self.chart_canvas.delete("all")
        
        if not data:
            self.chart_canvas.create_text(
                175, 200,
                text="No data available",
                font=("Segoe UI", 12),
                fill="#6a6a7a"
            )
            return
        
        # Calculate max value for scaling
        max_time = max(seconds for _, seconds in data)
        
        y_start = 20
        bar_height = 30
        spacing = 8
        max_bar_width = 250
        
        for idx, (app_name, seconds) in enumerate(data):
            y = y_start + idx * (bar_height + spacing)
            
            # Calculate bar width
            bar_width = (seconds / max_time) * max_bar_width if max_time > 0 else 0
            
            # Determine color based on category
            category = self.focus_calculator.get_app_category(app_name)
            if category == "productive":
                color = "#10b981"
            elif category == "distracting":
                color = "#ef4444"
            else:
                color = "#3b82f6"
            
            # Draw bar
            self.chart_canvas.create_rectangle(
                10, y,
                10 + bar_width, y + bar_height,
                fill=color,
                outline=""
            )
            
            # App name
            clean_name = app_name.replace(".exe", "")[:15]
            self.chart_canvas.create_text(
                15, y + bar_height // 2,
                text=clean_name,
                font=("Segoe UI", 9),
                fill="#ffffff",
                anchor="w"
            )
            
            # Time
            self.chart_canvas.create_text(
                max_bar_width + 30, y + bar_height // 2,
                text=self.format_time(seconds),
                font=("Segoe UI", 9, "bold"),
                fill="#ffffff",
                anchor="w"
            )
    
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
    
    def export_csv(self):
        """Export data to CSV"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"screen_time_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if file_path:
                usage_data = self.database.get_today_usage()
                
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Rank", "Application", "Category", "Time (seconds)", "Time (formatted)"])
                    
                    for idx, (app_name, seconds) in enumerate(usage_data, 1):
                        category = self.focus_calculator.get_app_category(app_name)
                        writer.writerow([
                            idx,
                            app_name,
                            category,
                            seconds,
                            self.format_time(seconds)
                        ])
                
                messagebox.showinfo("Success", f"Data exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def start_focus_session(self):
        """Start a focus session (placeholder)"""
        messagebox.showinfo(
            "Focus Session",
            "🎯 Focus Session Feature\n\n"
            "This feature will:\n"
            "• Block distracting apps\n"
            "• Set a focus timer\n"
            "• Track productivity\n\n"
            "Coming soon!"
        )
    
    def run(self):
        """Run dashboard"""
        self.root.mainloop()
