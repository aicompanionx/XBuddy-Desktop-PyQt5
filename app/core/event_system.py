from PyQt5.QtCore import QObject, pyqtSignal

class EventSystem(QObject):
    """Event system for inter-component communication"""

    # Define event signals
    model_changed = pyqtSignal(str)           # Model change
    interaction = pyqtSignal(str, object)     # User interaction
    api_response = pyqtSignal(str, object)    # API response

    _instance = None

    def __init__(self):
        super().__init__()

    @staticmethod
    def instance():
        """Singleton pattern"""
        if EventSystem._instance is None:
            EventSystem._instance = EventSystem()
        return EventSystem._instance
