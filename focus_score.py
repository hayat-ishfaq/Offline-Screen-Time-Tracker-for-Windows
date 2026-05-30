"""
Focus Score module for calculating productivity scores
"""
import json
import os


class FocusScoreCalculator:
    def __init__(self, config_file="apps_config.json"):
        """
        Initialize the Focus Score calculator
        
        Args:
            config_file: Path to the JSON configuration file mapping apps to categories
        """
        self.config_file = os.path.join(os.path.dirname(__file__), config_file)
        self.app_categories = self.load_config()

    def load_config(self):
        """
        Load app categorization from JSON config file
        
        Returns:
            Dictionary mapping app names to categories
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                print(f"Warning: {self.config_file} not found. Using default empty config.")
                return {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def get_app_category(self, app_name):
        """
        Get the category for a given app
        
        Args:
            app_name: Name of the application
            
        Returns:
            Category string: 'productive', 'neutral', or 'distracting'
        """
        # Check exact match first
        if app_name in self.app_categories:
            return self.app_categories[app_name]
        
        # Check case-insensitive match
        for config_app, category in self.app_categories.items():
            if config_app.lower() == app_name.lower():
                return category
        
        # Default to neutral if not found
        return "neutral"

    def calculate_category_totals(self, usage_data):
        """
        Calculate total time for each category
        
        Args:
            usage_data: List of tuples (app_name, total_seconds)
            
        Returns:
            Dictionary with productive_time, neutral_time, distracting_time
        """
        totals = {
            'productive': 0,
            'neutral': 0,
            'distracting': 0
        }
        
        for app_name, total_seconds in usage_data:
            category = self.get_app_category(app_name)
            totals[category] += total_seconds
        
        return totals

    def calculate_focus_score(self, usage_data):
        """
        Calculate the focus score based on app usage
        
        Formula:
        score = (productive * 1.0 + neutral * 0.5 - distracting * 0.5) / total_time
        
        Args:
            usage_data: List of tuples (app_name, total_seconds)
            
        Returns:
            Dictionary containing:
                - score: Focus score percentage (0-100)
                - productive_time: Seconds spent on productive apps
                - neutral_time: Seconds spent on neutral apps
                - distracting_time: Seconds spent on distracting apps
                - total_time: Total seconds tracked
        """
        category_totals = self.calculate_category_totals(usage_data)
        
        productive_time = category_totals['productive']
        neutral_time = category_totals['neutral']
        distracting_time = category_totals['distracting']
        total_time = productive_time + neutral_time + distracting_time
        
        # Calculate score
        if total_time == 0:
            score_percentage = 0
        else:
            raw_score = (
                productive_time * 1.0 +
                neutral_time * 0.5 -
                distracting_time * 0.5
            ) / total_time
            
            # Convert to percentage (0-100)
            # Normalize: raw_score ranges from -0.5 to 1.0
            # Map to 0-100: add 0.5 to get 0-1.5, divide by 1.5, multiply by 100
            score_percentage = max(0, min(100, ((raw_score + 0.5) / 1.5) * 100))
        
        return {
            'score': round(score_percentage, 1),
            'productive_time': productive_time,
            'neutral_time': neutral_time,
            'distracting_time': distracting_time,
            'total_time': total_time
        }
