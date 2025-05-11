"""
Base class for Live2D widgets, handling OpenGL rendering and model initialization.
"""

import sys
from pathlib import Path
import OpenGL.GL as gl
from OpenGL.GL import glGetString, GL_VERSION, GL_SHADING_LANGUAGE_VERSION, GL_VENDOR, GL_RENDERER
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QOpenGLWidget

import live2d.v3 as live2d
from live2d.utils import log

# Import SimpleCanvas for rendering
from app.gui.widgets.simple_canvas import SimpleCanvas as Canvas

# Define resource directory
RESOURCES_DIRECTORY = Path(__file__).parent.parent.parent.parent.absolute() / 'resources'


class BaseLive2DWidget(QOpenGLWidget):
    """
    Base OpenGL widget for Live2D model rendering.
    Handles basic initialization, OpenGL setup, and model loading.
    """
    
    def __init__(self):
        super().__init__()
        
        # Will be initialized in initializeGL
        self.model = None
        self.canvas = None
        
        # Default model path
        self.model_path = str(RESOURCES_DIRECTORY / "models/Haru/Haru.model3.json")

        # Configure window properties
        self.setWindowTitle("Live2DCanvas")
        
        # Configure window for transparency and always-on-top without focus stealing
        self.setWindowFlags(
            Qt.FramelessWindowHint |      # Borderless window
            Qt.WindowStaysOnTopHint |     # Always on top
            Qt.Tool |                     # Do not show in taskbar
            Qt.NoDropShadowWindowHint |   # No shadow
            Qt.WindowDoesNotAcceptFocus   # Don't steal focus
        )
        
        # Enable transparent background
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set transparent background style
        self.setStyleSheet("background: transparent;")
        
        # Set initial size
        self.resize(300, 600)

    def initializeGL(self):
        """Initialize OpenGL context and load Live2D model."""
        super().initializeGL()
        
        # Print OpenGL information for debugging
        print("GL_VERSION:", glGetString(GL_VERSION).decode())
        try:
            print("GLSL_VERSION:", glGetString(GL_SHADING_LANGUAGE_VERSION).decode())
            print("GL_VENDOR:", glGetString(GL_VENDOR).decode())
            print("GL_RENDERER:", glGetString(GL_RENDERER).decode())
        except Exception as e:
            print(f"Error getting additional OpenGL info: {e}")
        
        # Initialize Live2D model rendering
        try:
            live2d.glInit()  # Use glInit for OpenGL initialization
        except Exception as e:
            print(f"Warning: glInit failed, trying glewInit: {e}")
            live2d.glewInit()
            
        # Create Live2D model
        self.model = live2d.LAppModel()
        self.model.LoadModelJson(self.model_path)

        # Initialize Canvas for rendering
        self.canvas = Canvas()
        print("Canvas created successfully")

        # Print model parameters for debugging
        for i in range(self.model.GetParameterCount()):
            param = self.model.GetParameter(i)
            log.Debug(
                param.id, param.type, param.value, param.max, param.min, param.default
            )

        # Start animation timer at 60 FPS
        self.startTimer(int(1000 / 60))

    def timerEvent(self, event):
        """Handle timer events for animation updates."""
        super().timerEvent(event)
        self.update()

    def on_draw(self):
        """Draw the Live2D model."""
        try:
            live2d.clearBuffer()
            self.model.Draw()
        except Exception as e:
            print(f"Error in on_draw: {e}")

    def paintGL(self):
        """OpenGL painting method called by Qt framework."""
        try:
            # Clear with transparency
            gl.glClearColor(0.0, 0.0, 0.0, 0.0)  # Fully transparent background
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            
            # Set up alpha blending for proper transparency
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
            
            # Call parent implementation and update model
            super().paintGL()
            self.model.Update()
            self.canvas.Draw(self.on_draw)
            
            # Restore OpenGL state
            gl.glDisable(gl.GL_BLEND)
        except Exception as e:
            print(f"Error in paintGL: {e}")

    def resizeGL(self, width, height):
        """Handle widget resize events."""
        try:
            super().resizeGL(width, height)
            self.model.Resize(width, height)
            self.canvas.SetSize(width, height)
        except Exception as e:
            print(f"Error in resizeGL: {e}") 