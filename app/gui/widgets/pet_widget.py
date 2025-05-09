from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QMouseEvent

from OpenGL.GL import *
from OpenGL.GLU import *

class PetWidget(QOpenGLWidget):
    """Widget for rendering the Live2D model using OpenGL"""
    
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        
        # Set focus policy to receive keyboard events
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Set attributes for OpenGL
        self.setMouseTracking(True)
        
        # Animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(16)  # ~60 FPS
        
        # Interaction variables
        self.last_mouse_pos = None
        self.is_dragging = False
    
    def initializeGL(self):
        """Initialize OpenGL"""
        # Set clear color (transparent background)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Initialize Live2D renderer through model manager
        if hasattr(self.app_manager, 'model_manager'):
            self.app_manager.model_manager.init_gl()
    
    def resizeGL(self, width, height):
        """Handle widget resize"""
        # Update viewport
        glViewport(0, 0, width, height)
        
        # Set projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, width, height, 0)
        
        # Set model view matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Update model manager
        if hasattr(self.app_manager, 'model_manager'):
            self.app_manager.model_manager.resize(width, height)
    
    def paintGL(self):
        """Render the scene"""
        # Clear the buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Render the Live2D model
        if hasattr(self.app_manager, 'model_manager'):
            self.app_manager.model_manager.render()
    
    @Slot()
    def update_animation(self):
        """Update animation state"""
        if hasattr(self.app_manager, 'model_manager'):
            self.app_manager.model_manager.update()
        self.update()  # Trigger repaint
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            # Check if interaction is enabled
            if self.app_manager.config_manager.get("behavior.interaction_enabled", True):
                self.is_dragging = True
                self.last_mouse_pos = event.pos()
                
                # Notify model manager about interaction
                if hasattr(self.app_manager, 'model_manager'):
                    self.app_manager.model_manager.on_tap(event.x(), event.y())
                
                # Emit interaction event
                self.app_manager.event_system.interaction.emit("tap", {"x": event.x(), "y": event.y()})
        
        # Pass event to parent for window dragging
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
        
        # Pass event to parent for window dragging
        super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events"""
        # Update model manager with mouse position
        if hasattr(self.app_manager, 'model_manager'):
            self.app_manager.model_manager.on_mouse_move(event.x(), event.y())
        
        # Pass event to parent for window dragging
        super().mouseMoveEvent(event) 