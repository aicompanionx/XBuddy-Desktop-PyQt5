import unittest
import sys
import os
import json
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.app_manager import AppManager
from app.core.config_manager import ConfigManager
from app.core.event_system import EventSystem

class TestConfigManager(unittest.TestCase):
    """Test the ConfigManager class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_config_path = "test_config.json"
        self.config_manager = ConfigManager()
        self.config_manager.config_path = self.test_config_path
    
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)
    
    def test_load_default_config(self):
        """Test loading default configuration"""
        self.config_manager.load_config()
        self.assertEqual(self.config_manager.get("model"), "default")
        self.assertEqual(self.config_manager.get("window.width"), 300)
        self.assertEqual(self.config_manager.get("window.height"), 400)
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration"""
        self.config_manager.load_config()
        self.config_manager.set("model", "test_model")
        self.config_manager.set("window.width", 500)
        
        # Create a new config manager to load from file
        new_config_manager = ConfigManager()
        new_config_manager.config_path = self.test_config_path
        new_config_manager.load_config()
        
        self.assertEqual(new_config_manager.get("model"), "test_model")
        self.assertEqual(new_config_manager.get("window.width"), 500)
    
    def test_get_nested_config(self):
        """Test getting nested configuration values"""
        self.config_manager.load_config()
        self.assertEqual(self.config_manager.get("window.width"), 300)
        self.assertEqual(self.config_manager.get("window.height"), 400)
        self.assertEqual(self.config_manager.get("behavior.auto_start"), False)
    
    def test_set_nested_config(self):
        """Test setting nested configuration values"""
        self.config_manager.load_config()
        self.config_manager.set("window.width", 500)
        self.config_manager.set("new.nested.value", "test")
        
        self.assertEqual(self.config_manager.get("window.width"), 500)
        self.assertEqual(self.config_manager.get("new.nested.value"), "test")


class TestEventSystem(unittest.TestCase):
    """Test the EventSystem class"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = QApplication.instance() or QApplication([])
        self.event_system = EventSystem.instance()
    
    def test_singleton(self):
        """Test that EventSystem is a singleton"""
        event_system2 = EventSystem.instance()
        self.assertIs(self.event_system, event_system2)
    
    def test_signals(self):
        """Test event signals"""
        # Set up signal handlers
        self.model_changed_called = False
        self.interaction_called = False
        self.api_response_called = False
        
        def on_model_changed(model_id):
            self.model_changed_called = True
            self.assertEqual(model_id, "test_model")
        
        def on_interaction(interaction_type, data):
            self.interaction_called = True
            self.assertEqual(interaction_type, "tap")
            self.assertEqual(data["x"], 100)
            self.assertEqual(data["y"], 200)
        
        def on_api_response(endpoint, data):
            self.api_response_called = True
            self.assertEqual(endpoint, "test")
            self.assertEqual(data["status"], "ok")
        
        # Connect signals
        self.event_system.model_changed.connect(on_model_changed)
        self.event_system.interaction.connect(on_interaction)
        self.event_system.api_response.connect(on_api_response)
        
        # Emit signals
        self.event_system.model_changed.emit("test_model")
        self.event_system.interaction.emit("tap", {"x": 100, "y": 200})
        self.event_system.api_response.emit("test", {"status": "ok"})
        
        # Check that handlers were called
        self.assertTrue(self.model_changed_called)
        self.assertTrue(self.interaction_called)
        self.assertTrue(self.api_response_called)


if __name__ == "__main__":
    unittest.main() 