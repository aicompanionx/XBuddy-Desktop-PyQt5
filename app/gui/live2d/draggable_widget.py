"""
Draggable Live2D widget implementation with mouse interaction.
Enables dragging the window by clicking on the Live2D model.
"""

import OpenGL.GL as gl
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import QPoint, Qt

from app.gui.live2d.penetration_widget import PenetrationLive2DWidget


class DraggableLive2DWidget(PenetrationLive2DWidget):
    """
    Live2D widget with window dragging capabilities.
    Allows the user to move the entire window by clicking and dragging
    on the visible model area.
    """
    
    def __init__(self):
        super().__init__()
        # Window dragging state
        self.window_dragging = False
        self.drag_start_pos = None
        
        # Set mouse tracking to improve drag responsiveness
        self.setMouseTracking(True)
        
        # Track cleanup state
        self._drag_cleaned_up = False

    def isInModelArea(self, x, y):
        """
        Check if the given screen coordinates are within the visible model area.
        Uses OpenGL to read pixel alpha value at the given coordinates.
        
        Args:
            x (int): X coordinate in widget space
            y (int): Y coordinate in widget space
            
        Returns:
            bool: True if point is within model area (non-transparent)
        """
        # Skip if cleaned up
        if hasattr(self, '_drag_cleaned_up') and self._drag_cleaned_up:
            return False
            
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
        Handle mouse press events to start window dragging.
        Start dragging the window when clicking on the model area.
        """
        # Skip if cleaned up
        if hasattr(self, '_drag_cleaned_up') and self._drag_cleaned_up:
            return
            
        try:
            # Call parent for any base functionality
            super().mousePressEvent(event)
            
            x, y = event.x(), event.y()
            print(f'Mouse pressed at {x}, {y}')
            
            # Check if mouse is over the model's visible area
            if self.isInModelArea(x, y):
                # Start window dragging
                self.window_dragging = True
                # Store the initial mouse position relative to the window
                self.drag_start_pos = event.globalPos() - self.window().frameGeometry().topLeft()
                
                # Change cursor to indicate dragging is in progress
                # This is optional but provides visual feedback
                self.setCursor(Qt.ClosedHandCursor)
        except Exception as e:
            print(f"Error in mousePressEvent: {e}")

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Handle mouse move events for window dragging.
        Move the entire window when dragging.
        """
        # Skip if cleaned up
        if hasattr(self, '_drag_cleaned_up') and self._drag_cleaned_up:
            return
            
        try:
            # Call parent for any base functionality
            super().mouseMoveEvent(event)
            
            # If we're in window dragging mode, move the window
            if self.window_dragging:
                # Calculate new window position
                new_pos = event.globalPos() - self.drag_start_pos
                
                # Move the window (not just this widget)
                self.window().move(new_pos)
                
                print(f'Window moved to {new_pos.x()}, {new_pos.y()}')
        except Exception as e:
            print(f"Error in mouseMoveEvent: {e}")

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Handle mouse release events to end window dragging.
        """
        # Skip if cleaned up
        if hasattr(self, '_drag_cleaned_up') and self._drag_cleaned_up:
            return
            
        try:
            # Call parent for any base functionality
            super().mouseReleaseEvent(event)
            
            # End window dragging
            if self.window_dragging:
                self.window_dragging = False
                self.drag_start_pos = None
                
                # Restore cursor
                self.setCursor(Qt.ArrowCursor)
                
                print('Window drag complete')
        except Exception as e:
            print(f"Error in mouseReleaseEvent: {e}")
            
    def moveEvent(self, event):
        """
        Handle widget move events.
        Called when the widget is moved to track position.
        """
        # Skip if cleaned up
        if hasattr(self, '_drag_cleaned_up') and self._drag_cleaned_up:
            return
            
        new_pos = event.pos()
        print(f'Widget position changed: {new_pos.x()}, {new_pos.y()}')
        super().moveEvent(event)
        
    def cleanup(self):
        """Clean up resources before destruction."""
        if hasattr(self, '_drag_cleaned_up') and self._drag_cleaned_up:
            return
            
        print("Cleaning up draggable widget")
        self._drag_cleaned_up = True
        self.window_dragging = False
        self.drag_start_pos = None
        
        # Call parent cleanup if available
        if hasattr(super(), 'cleanup'):
            super().cleanup()
            
    def __del__(self):
        """Ensure cleanup when object is destroyed."""
        self.cleanup() 