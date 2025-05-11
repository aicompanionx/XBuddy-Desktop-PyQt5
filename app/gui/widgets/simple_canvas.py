
import OpenGL.GL as gl

class SimpleCanvas:
    """A simplified canvas for rendering that doesn't use VAOs (compatible with OpenGL 2.1)."""
    
    def __init__(self):
        """Initialize canvas."""
        self.width = 0
        self.height = 0
        print("SimpleCanvas initialized")
    
    def SetSize(self, width, height):
        """Set canvas dimensions.
        
        Args:
            width: Canvas width
            height: Canvas height
        """
        self.width = width
        self.height = height
        print(f"Canvas size set to {width}x{height}")
    
    def Draw(self, callback):
        """Draw content using the callback function.
        
        Args:
            callback: Function to call for drawing
        """
        if callable(callback):
            # Clear the canvas with transparent background
            gl.glClearColor(0.0, 0.0, 0.0, 0.0)  # RGBA, fully transparent
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            
            # Configure OpenGL state for transparent rendering
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
            
            # Execute drawing callback
            try:
                callback()
            except Exception as e:
                print(f"Error during drawing: {e}")
            
            # Reset OpenGL state
            gl.glDisable(gl.GL_BLEND)
