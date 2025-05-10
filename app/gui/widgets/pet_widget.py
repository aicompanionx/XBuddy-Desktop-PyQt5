from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QMouseEvent

from OpenGL.GL import *
from OpenGL.GLU import *


class PetWidget(QOpenGLWidget):
    """Widget for rendering the Live2D model using OpenGL"""

    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager

        # Enable mouse tracking and keyboard focus
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

        # Animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(16)  # ~60 FPS

        self.last_mouse_pos = None
        self.is_dragging = False

    def initializeGL(self):
        """Initialize OpenGL"""
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        if hasattr(self.app_manager, 'model_manager'):
            self.app_manager.model_manager.init_gl()

    def resizeGL(self, width, height):
        """Handle widget resize"""
        glViewport(0, 0, width, height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, width, height, 0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        if hasattr(self.app_manager, 'model_manager'):
            self.app_manager.model_manager.resize(width, height)

    def paintGL(self):
        """Render the scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if hasattr(self.app_manager, 'model_manager'):
            self.app_manager.model_manager.render()

    @pyqtSlot()
    def update_animation(self):
        """Update animation state"""
        if hasattr(self.app_manager, 'model_manager'):
            self.app_manager.model_manager.update()
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if self.app_manager.config_manager.get("behavior.interaction_enabled", True):
                self.is_dragging = True
                self.last_mouse_pos = event.pos()

                if hasattr(self.app_manager, 'model_manager'):
                    self.app_manager.model_manager.on_tap(event.x(), event.y())

                self.app_manager.event_system.interaction.emit("tap", {"x": event.x(), "y": event.y()})

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if hasattr(self.app_manager, 'model_manager'):
            self.app_manager.model_manager.on_mouse_move(event.x(), event.y())
        super().mouseMoveEvent(event)
