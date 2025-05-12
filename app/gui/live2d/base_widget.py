"""
Base class for Live2D widgets, handling OpenGL rendering and model initialization.
"""
import os
import sys
from pathlib import Path
import OpenGL.GL as gl
from OpenGL.GL import glGetString, GL_VERSION, GL_SHADING_LANGUAGE_VERSION, GL_VENDOR, GL_RENDERER
from PyQt5.QtCore import Qt, QTimer
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
    def find_model3_json_files(self, root_dir):
        model_files = []
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith("model3.json"):
                    model_files.append(os.path.join(dirpath, filename))
        return model_files
    
    def __init__(self):
        super().__init__()
        
        # Will be initialized in initializeGL
        self.model = None
        self.canvas = None

        self.model_list = self.find_model3_json_files(RESOURCES_DIRECTORY / "models")
        # Default model path
        self.model_path = str(RESOURCES_DIRECTORY / "models/Haru/Haru.model3.json")

        # Configure window properties
        self.setWindowTitle("Live2DCanvas")
        # Set initial size
        self.resize(300, 600)
        
        # Track if we've initialized
        self.is_initialized = False
        
        # Prevent redundant cleanup
        self.is_cleaned_up = False
        
        # Store device pixel ratio for high DPI scaling
        self.pixel_ratio = self.devicePixelRatio() * 2
        
        # Custom scale factor for additional clarity control
        self.custom_scale_factor = 1.0
        
        # Store timer IDs for cleanup
        self.timer_ids = []

    def setScaleFactor(self, scale_factor):
        """
        Set a custom scale factor to adjust model clarity.
        
        Args:
            scale_factor (float): Scale factor value (1.0 is default, >1.0 increases clarity)
        """
        if scale_factor <= 0:
            print("Warning: Scale factor must be positive, ignoring value")
            return
            
        self.custom_scale_factor = scale_factor
        print(f"Custom scale factor set to: {scale_factor}")
        
        # Force resize to apply the new scale factor
        if self.is_initialized and not self.is_cleaned_up:
            self.resizeGL(self.width(), self.height())
            self.update()

    def getEffectiveScale(self):
        """
        Get the effective scale factor (device pixel ratio * custom scale).
        
        Returns:
            float: The effective scale factor
        """
        return self.pixel_ratio * self.custom_scale_factor

    def initializeGL(self):
        """Initialize OpenGL context and load Live2D model."""
        super().initializeGL()
        
        try:
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
            self.model.SetScale(0.5)

            # Initialize Canvas for rendering
            self.canvas = Canvas()
            print("Canvas created successfully")
            
            # Print device pixel ratio for debugging
            print(f"Device pixel ratio: {self.pixel_ratio}")
            print(f"Custom scale factor: {self.custom_scale_factor}")
            print(f"Effective scale: {self.getEffectiveScale()}")

            # Print model parameters for debugging
            try:
                if self.model and hasattr(self.model, 'GetParameterCount'):
                    for i in range(self.model.GetParameterCount()):
                        param = self.model.GetParameter(i)
                        log.Debug(
                            param.id, param.type, param.value, param.max, param.min, param.default
                        )
            except Exception as e:
                print(f"Error getting model parameters: {e}")

            # Start animation timer at 60 FPS
            timer_id = self.startTimer(int(1000 / 60))
            self.timer_ids.append(timer_id)
            
            # Mark as initialized
            self.is_initialized = True
        except Exception as e:
            print(f"Error in initializeGL: {e}")
            self.is_initialized = False

    def startTimer(self, interval):
        """Override to keep track of timer IDs."""
        timer_id = super().startTimer(interval)
        self.timer_ids.append(timer_id)
        return timer_id

    def timerEvent(self, event):
        """Handle timer events for animation updates."""
        if not self.is_initialized or self.is_cleaned_up:
            return
            
        try:
            super().timerEvent(event)
            self.update()
        except Exception as e:
            print(f"Error in base timerEvent: {e}")

    def on_draw(self):
        """Draw the Live2D model."""
        if not self.model or self.is_cleaned_up:
            return
            
        try:
            if hasattr(live2d, 'clearBuffer'):
                live2d.clearBuffer()
            if hasattr(self.model, 'Draw'):
                self.model.Draw()
        except Exception as e:
            print(f"Error in on_draw: {e}")

    def paintGL(self):
        """OpenGL painting method called by Qt framework."""
        if not self.is_initialized or self.is_cleaned_up:
            return
            
        try:
            # Clear with transparency
            gl.glClearColor(0.0, 0.0, 0.0, 0.0)  # Fully transparent background
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            
            # Set up alpha blending for proper transparency
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
            
            # Call parent implementation and update model
            super().paintGL()
            
            if self.model and self.canvas:
                if hasattr(self.model, 'Update'):
                    self.model.Update()
                if hasattr(self.canvas, 'Draw'):
                    self.canvas.Draw(self.on_draw)
            
            # Restore OpenGL state
            gl.glDisable(gl.GL_BLEND)
        except Exception as e:
            print(f"Error in paintGL: {e}")

    def resizeGL(self, width, height):
        """Handle widget resize events."""
        if not self.is_initialized or self.is_cleaned_up:
            return
            
        try:
            super().resizeGL(width, height)
            
            # Update device pixel ratio in case it changed
            self.pixel_ratio = self.devicePixelRatio()
            
            # Apply device pixel ratio scaling for high DPI displays
            # Combined with custom scale factor
            effective_scale = self.getEffectiveScale()
            scaled_width = int(width * effective_scale)
            scaled_height = int(height * effective_scale)
            
            print(f"Resizing with effective scale {effective_scale}: {width}x{height} -> {scaled_width}x{scaled_height}")

            if self.model and hasattr(self.model, 'Resize'):
                # Resize model with scaled dimensions
                self.model.Resize(scaled_width, scaled_height)
            if self.canvas and hasattr(self.canvas, 'SetSize'):
                self.canvas.SetSize(scaled_width, scaled_height)
        except Exception as e:
            print(f"Error in resizeGL: {e}")
    
    def stop_timers(self):
        """Stop all timers to prevent callbacks after cleanup."""
        for timer_id in self.timer_ids:
            try:
                self.killTimer(timer_id)
            except Exception as e:
                print(f"Error stopping timer {timer_id}: {e}")
        self.timer_ids.clear()
            
    def cleanup_resources(self):
        """Clean up OpenGL resources to prevent memory leaks."""
        if self.is_cleaned_up:
            return
            
        print("Cleaning up base widget resources")
        
        try:
            # Mark as cleaned up to prevent further rendering
            self.is_cleaned_up = True
            
            # Stop all timers first
            self.stop_timers()
            
            # Clear model reference (actual disposal is handled by Live2D manager)
            self.model = None
            
            # Clear canvas
            if self.canvas:
                self.canvas = None
        except Exception as e:
            print(f"Error in cleanup_resources: {e}")
            
    def cleanup(self):
        """Clean up all resources."""
        if self.is_cleaned_up:
            return
            
        print("Base widget cleanup")
        self.cleanup_resources()
            
    def __del__(self):
        """Ensure proper cleanup when object is destroyed."""
        self.cleanup() 