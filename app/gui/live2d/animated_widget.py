"""
Animated Live2D widget with motion and keyboard control support.
"""

from PyQt5.QtGui import QKeyEvent, QCursor
from PyQt5.QtCore import Qt

from live2d.utils import log
from app.gui.live2d.draggable_widget import DraggableLive2DWidget


class AnimatedLive2DWidget(DraggableLive2DWidget):
    """
    Live2D widget with animation and motion capabilities.
    Adds support for:
    - Keyboard control of model position
    - Automatic mouse tracking for head/eye movement
    - Motion and expression triggering
    """
    
    def __init__(self):
        super().__init__()
        
        # Model position offset
        self.dx = 0.0
        self.dy = 0.0
        
        # Flag to control mouse tracking
        self.tracking_enabled = True
        
        # Flag to track if cleanup has been done
        self._is_cleaned_up = False

    def initializeGL(self):
        """Initialize OpenGL and print model information."""
        super().initializeGL()
        
        # Print canvas size information for debugging
        if self.model:
            try:
                print("Canvas size:", self.model.GetCanvasSize())
                print("Canvas size in pixels:", self.model.GetCanvasSizePixel())
                print("Pixels per unit:", self.model.GetPixelsPerUnit())
            except Exception as e:
                print(f"Error getting model info: {e}")

    def follow_mouse(self):
        """Make the model look at the mouse cursor position."""
        # Only track if enabled and not cleaned up
        if not self.tracking_enabled or self._is_cleaned_up:
            return
            
        try:
            # Get global cursor position
            global_pos = QCursor.pos()
            
            # Convert global position to local widget coordinates
            local_pos = self.mapFromGlobal(global_pos)
            
            # Update model to look at this position
            if self.model and hasattr(self.model, 'Drag'):
                self.model.Drag(local_pos.x(), local_pos.y())
        except Exception as e:
            print(f"Error in follow_mouse: {e}")
            self.tracking_enabled = False  # Disable on error

    def timerEvent(self, event):
        """
        Handle timer events for animation.
        Updates model position and cursor tracking.
        """
        # Skip if cleaned up or model is None/invalid
        if self._is_cleaned_up:
            return
            
        # Skip if model is None or invalid
        if not self.model or not hasattr(self.model, 'SetOffset'):
            return
            
        try:
            # Apply position offset to model
            self.model.SetOffset(self.dx, self.dy)
            
            # Make model follow mouse cursor
            self.follow_mouse()
            
            # Call parent implementation
            try:
                super().timerEvent(event)
            except Exception as e:
                print(f"Error in parent timerEvent: {e}")
        except Exception as e:
            print(f"Error in animated widget timerEvent: {e}")
            # Disable tracking on error to prevent further issues
            self.tracking_enabled = False

    def stop_animations(self):
        """Stop all animations and motions."""
        self.tracking_enabled = False
        if not self._is_cleaned_up and self.model and hasattr(self.model, 'StopAllMotions'):
            try:
                self.model.StopAllMotions()
            except Exception as e:
                print(f"Error stopping motions: {e}")
                
    def cleanup(self):
        """Clean up resources to prevent memory leaks."""
        if self._is_cleaned_up:
            return
            
        print("Cleaning up animated widget")
        self._is_cleaned_up = True
        self.tracking_enabled = False
        
        # Call parent cleanup if available
        if hasattr(super(), 'cleanup'):
            super().cleanup()

    def keyPressEvent(self, event: QKeyEvent):
        """
        Handle keyboard input for controlling the model.
        
        Keys:
        - Arrow keys: move model position
        - R: reset pose
        - E: reset expression
        """
        super().keyPressEvent(event)
        
        # Skip if model is None or cleaned up
        if self._is_cleaned_up or not self.model:
            return
            
        # Handle arrow keys to move model
        if event.key() == Qt.Key_Left:
            self.dx -= 0.1
        elif event.key() == Qt.Key_Right:
            self.dx += 0.1
        elif event.key() == Qt.Key_Up:
            self.dy += 0.1
        elif event.key() == Qt.Key_Down:
            self.dy -= 0.1
            
        # Reset pose and expression
        elif event.key() == Qt.Key_R:
            if hasattr(self.model, 'StopAllMotions') and hasattr(self.model, 'ResetPose'):
                self.model.StopAllMotions()
                self.model.ResetPose()
        elif event.key() == Qt.Key_E:
            if hasattr(self.model, 'ResetExpression'):
                self.model.ResetExpression()

    def on_start_motion_callback(self, group, no):
        """Callback when motion starts."""
        log.Info(f"Start motion: [{group}_{no}]")

    def on_finish_motion_callback(self):
        """Callback when motion finishes."""
        log.Info("Motion finished")

    def mousePressEvent(self, event):
        """
        Handle mouse press events.
        In addition to dragging, trigger random expression and motion.
        """
        super().mousePressEvent(event)
        
        # Skip if model is None or cleaned up
        if self._is_cleaned_up or not self.model:
            return
            
        try:
            # Set random expression
            if hasattr(self.model, 'SetRandomExpression'):
                self.model.SetRandomExpression()
            
            # Start random motion with callbacks
            if hasattr(self.model, 'StartRandomMotion'):
                self.model.StartRandomMotion(
                    priority=3,
                    onStartMotionHandler=self.on_start_motion_callback,
                    onFinishMotionHandler=self.on_finish_motion_callback)
        except Exception as e:
            print(f"Error in mousePressEvent animation: {e}")
            
    def __del__(self):
        """Ensure cleanup when object is destroyed."""
        self.cleanup() 