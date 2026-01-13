"""
Data Manager - Handles local file storage
"""
import json
import os
from datetime import datetime
from config.settings import DATA_FILE


class DataManager:
    """Manages local JSON file storage"""
    
    def __init__(self):
        self.data_file = DATA_FILE
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Create data file if it doesn't exist"""
        if not os.path.exists(self.data_file):
            default_data = {
                "settings": {
                    "theme": "dark",
                    "last_opened": None
                },
                "tools": [],
                "recent_tools": [],
                "favorites": [],
                "created_at": datetime.now().isoformat()
            }
            self.save_data(default_data)
    
    def load_data(self):
        """Load data from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
            return {}
    
    def save_data(self, data):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def update_setting(self, key, value):
        """Update a specific setting"""
        data = self.load_data()
        if "settings" not in data:
            data["settings"] = {}
        data["settings"][key] = value
        return self.save_data(data)
    
    def get_setting(self, key, default=None):
        """Get a specific setting"""
        data = self.load_data()
        return data.get("settings", {}).get(key, default)
    
    def add_recent_tool(self, tool_name):
        """Add tool to recent tools list"""
        data = self.load_data()
        recent = data.get("recent_tools", [])
        
        # Remove if already exists
        if tool_name in recent:
            recent.remove(tool_name)
        
        # Add to front
        recent.insert(0, tool_name)
        
        # Keep only last 10
        data["recent_tools"] = recent[:10]
        
        return self.save_data(data)
    
    def get_recent_tools(self):
        """Get list of recent tools"""
        data = self.load_data()
        return data.get("recent_tools", [])
    
    def toggle_favorite(self, tool_name):
        """Add or remove tool from favorites"""
        data = self.load_data()
        favorites = data.get("favorites", [])
        
        if tool_name in favorites:
            favorites.remove(tool_name)
        else:
            favorites.append(tool_name)
        
        data["favorites"] = favorites
        return self.save_data(data)
    
    def get_favorites(self):
        """Get list of favorite tools"""
        data = self.load_data()
        return data.get("favorites", [])