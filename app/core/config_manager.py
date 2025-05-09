import json
import os
from PySide6.QtCore import QObject, Signal

from dotenv import load_dotenv

load_dotenv()

class ConfigManager(QObject):
    """Configuration manager responsible for loading and saving configuration"""
    
    config_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.config_path = "config.json"
        self.config = {}
        self.default_config = {
            "model": "default",
            "window": {
                "width": 300,
                "height": 400,
                "x": 100,
                "y": 100,
                "always_on_top": True,
                "transparent": True
            },
            "behavior": {
                "auto_start": False,
                "follow_cursor": False,
                "interaction_enabled": True
            },
            "api": {
                "base_url": os.getenv("API_BASE_URL"),
                "timeout": 10
            }
        }
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            else:
                self.config = self.default_config.copy()
                self.save_config()
        except Exception as e:
            print(f"Failed to load configuration: {e}")
            self.config = self.default_config.copy()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            self.config_changed.emit()
        except Exception as e:
            print(f"Failed to save configuration: {e}")
    
    def get(self, key, default=None):
        """Get configuration item by key"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key, value):
        """Set configuration item by key"""
        keys = key.split(".")
        config = self.config
        for i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config() 