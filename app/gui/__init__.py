"""
GUI module for XBuddy Desktop application.
Includes components for the main interface and Live2D models.
"""

# Directly expose the PetWidget and run function from live2d module
from app.gui.live2d import PetWidget, run

__all__ = ['PetWidget', 'run']
