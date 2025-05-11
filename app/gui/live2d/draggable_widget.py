"""
Draggable Live2D widget implementation with mouse interaction.
"""

import OpenGL.GL as gl
from PyQt5.QtGui import QMouseEvent

from app.gui.live2d.base_widget import BaseLive2DWidget


class DraggableLive2DWidget(BaseLive2DWidget):
    """
    Live2D widget with dragging capabilities.
    Allows the user to move the widget by clicking and dragging on model areas.
    """
    
    def __init__(self):
        super().__init__()
        # Dragging state
        self.dragging = False
        self.drag_offset = None

    def isInModelArea(self, x, y):
        """
        Check if the given screen coordinates are within the visible model area.
        Uses OpenGL to read pixel alpha value at the given coordinates.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            bool: True if point is within model area (non-transparent)
        """
        try:
            h = self.height()
            px = int(x)
            py = int((h - y))  # Convert to OpenGL coordinate system
            
            # Read pixel color data (RGBA) at the specified point
            data = gl.glReadPixels(px, py, 1, 1, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)
            
            # Check alpha component (4th component)
            alpha = data[3]
            
            # Return true if point has any opacity
            return alpha > 0
        except Exception as e:
            print(f"Error in isInModelArea: {e}")
            return True  # Default to True on error for better UX

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handle mouse press events for dragging.
        Start dragging when clicking on the model area.
        """
        try:
            super().mousePressEvent(event)
            x, y = event.x(), event.y()
            print(f'Pressed {x}, {y}')
            
            # Check if mouse is over the model
            if self.isInModelArea(x, y):
                self.dragging = True
                self.drag_offset = event.globalPos() - self.pos()
        except Exception as e:
            print(f"Error in mousePressEvent: {e}")

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Handle mouse move events for dragging.
        Move the widget when dragging.
        """
        try:
            super().mouseMoveEvent(event)
            x, y = event.x(), event.y()
            print(f'Moved {x}, {y}')
            
            # Move the widget if dragging
            if self.dragging:
                self.move(event.globalPos() - self.drag_offset)
        except Exception as e:
            print(f"Error in mouseMoveEvent: {e}")

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Handle mouse release events to end dragging.
        """
        try:
            super().mouseReleaseEvent(event)
            x, y = event.x(), event.y()
            print(f'Released {x}, {y}')
            
            # End dragging
            if self.dragging:
                self.dragging = False
        except Exception as e:
            print(f"Error in mouseReleaseEvent: {e}") 