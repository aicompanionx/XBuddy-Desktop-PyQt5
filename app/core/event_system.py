from PySide6.QtCore import QObject, Signal

class EventSystem(QObject):
    """Event system for inter-component communication"""
    
    # Define event signals
    model_changed = Signal(str)  # Model change
    interaction = Signal(str, object)  # User interaction
    api_response = Signal(str, object)  # API response
    
    _instance = None
    
    def __init__(self):
        super().__init__()
        
    @staticmethod
    def instance():
        """Singleton pattern"""
        if EventSystem._instance is None:
            EventSystem._instance = EventSystem()
        return EventSystem._instance 