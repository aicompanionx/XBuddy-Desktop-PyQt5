"""
Desktop pet widget implementation that stays on top without stealing focus.
"""

import sys
import platform
from PyQt5.QtCore import Qt, QEvent, QTimer, QCoreApplication
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QSurfaceFormat

import live2d.v3 as live2d
from app.gui.live2d.button_widget import ButtonLive2DWidget


class PetWidget(ButtonLive2DWidget):
    """
    Final desktop pet widget implementation.
    Handles window-level behaviors:
    - Staying on top without stealing focus
    - Platform-specific window configurations
    - Preventing window from being hidden when losing focus
    """
    
    def __init__(self):
        super().__init__()
        # Store timers for proper cleanup
        self.timers = []
        
        # Ensure window stays on top but doesn't steal focus
        self.setWindowFlags(
            self.windowFlags() | 
            Qt.WindowStaysOnTopHint |     # Always on top
            Qt.WindowDoesNotAcceptFocus   # Don't steal keyboard focus
        )
        
        # Platform-specific configurations
        self._configure_platform_specific()
        
        # Prevent window from being minimized
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinimizeButtonHint)
        
        # Set attribute to prevent taking focus when shown
        self.setAttribute(Qt.WA_ShowWithoutActivating)

    def _configure_platform_specific(self):
        """Apply platform-specific window configurations."""
        # For Linux, use X11 bypass to avoid window manager interference
        if platform.system() == "Linux":
            self.setWindowFlags(self.windowFlags() | Qt.X11BypassWindowManagerHint)
        
        # For macOS, use opacity trick for better stacking
        elif platform.system() == "Darwin":
            try:
                # Almost fully opaque, triggers proper layer ordering on macOS
                self.setWindowOpacity(0.999)
                print("Applied macOS window opacity trick for better stacking")
            except Exception as e:
                print(f"Failed to apply macOS window trick: {e}")

    def startTimer(self, interval):
        """Override startTimer to keep track of timers for proper cleanup."""
        timer_id = super().startTimer(interval)
        self.timers.append(timer_id)
        return timer_id

    def stopAllTimers(self):
        """Stop all active timers to prevent callbacks after destruction."""
        for timer_id in self.timers:
            self.killTimer(timer_id)
        self.timers.clear()
        
    def cleanup(self):
        """Perform thorough cleanup before destruction."""
        if hasattr(self, '_cleanup_called') and self._cleanup_called:
            return
        
        print("Performing thorough widget cleanup")
        self._cleanup_called = True
            
        # Stop all timers first to prevent any further callbacks
        self.stopAllTimers()
        
        # Call cleanup methods from each layer
        try:
            # 1. LipSync cleanup
            if hasattr(self, 'cleanup_lip_sync'):
                self.cleanup_lip_sync()
            
            # 2. Animation cleanup
            if hasattr(self, 'stop_animations'):
                self.stop_animations()
                
            # 3. Base resources cleanup
            if hasattr(self, 'cleanup_resources'):
                self.cleanup_resources()
        except Exception as e:
            print(f"Error during cleanup: {e}")
        
        # Set references to None
        self.model = None
        self.canvas = None

    def showEvent(self, event):
        """
        Override show event to ensure window is shown properly.
        Avoids stealing focus when shown.
        """
        super().showEvent(event)
        # Don't call raise_() or activateWindow() to avoid stealing focus

    def closeEvent(self, event):
        """
        Handle close event to prevent actual window closing.
        Just hides the window instead.
        """
        # Clean up resources first
        self.cleanup()
        
        # Prevent actual closing
        event.ignore()
        
        # Just hide the window
        self.hide()

    def event(self, event):
        """
        Filter window events to manage focus and visibility.
        Prevents focus stealing and ensures window remains visible.
        """
        # Block activation/focus events
        if event.type() in [QEvent.WindowActivate, QEvent.FocusIn]:
            return True  # Block these events
        
        # Handle window losing focus
        elif event.type() == QEvent.WindowDeactivate:
            # Ensure the window remains visible when losing focus
            self.setVisible(True)
            
        # For other events, use default handling
        return super().event(event)

    def changeEvent(self, event):
        """
        Handle window state change events.
        Prevents the window from staying minimized.
        """
        if event.type() == QEvent.WindowStateChange:
            # If window gets minimized, restore it
            if self.windowState() & Qt.WindowMinimized:
                # Use timer to avoid immediate conflicts with OS
                QTimer.singleShot(100, self._restore_window)
        
        # Call parent implementation
        super().changeEvent(event)

    def _restore_window(self):
        """
        Restore window from minimized state without stealing focus.
        """
        # Clear minimized state
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized)
        
        # Show window without stealing focus
        self.show()
        
    def __del__(self):
        """Ensure proper cleanup when object is garbage collected."""
        self.cleanup()


class Application(QApplication):
    """
    Custom application class with enhanced event handling.
    Ensures proper window behavior and prevents focus stealing.
    """
    
    def __init__(self, argv):
        super().__init__(argv)
        self.pet_widget = None

        # Don't quit when window is closed
        self.setQuitOnLastWindowClosed(False)

        # Disable context help button on window titlebars
        self.setAttribute(Qt.AA_DisableWindowContextHelpButton)

    def register_pet_widget(self, widget):
        """Register the pet widget for proper cleanup."""
        self.pet_widget = widget

    def event(self, event):
        """Handle application-level events"""
        # Intercept close events to prevent unwanted application termination
        if event.type() == QEvent.Close:
            print("System close event intercepted - preventing close")
            return True  # Block the close event

        # Handle desktop session events (logout/shutdown)
        if hasattr(QEvent, 'ApplicationStateChange') and event.type() == QEvent.ApplicationStateChange:
            print("Application state changed, ensuring windows remain visible")

            # Ensure all windows remain visible
            for window in self.topLevelWidgets():
                if window.isVisible():
                    # Restore from minimized state without activating
                    if window.windowState() & Qt.WindowMinimized:
                        window.setWindowState(window.windowState() & ~Qt.WindowMinimized)

                    # Don't call raise_() or activateWindow() to avoid stealing focus

        # Handle application quit properly with cleanup
        # if event.type() == QEvent.Quit:
        #     # Perform cleanup before actually quitting
        #     if self.pet_widget:
        #         self.pet_widget.cleanup()

        # Block activation events to prevent focus stealing
        if event.type() in [QEvent.ApplicationActivate, QEvent.WindowActivate, QEvent.FocusIn]:
            return True  # Block these events

        # Pass other events to default handler
        return super().event(event)

    def __del__(self):
        """Clean up application resources."""
        if self.pet_widget:
            self.pet_widget.cleanup()


def configure_opengl():
    """Configure OpenGL settings for the application"""
    # Create and configure OpenGL surface format
    fmt = QSurfaceFormat()
    
    # Set OpenGL version to 2.1 for compatibility with Live2D
    fmt.setVersion(2, 1)
    
    # Use compatibility profile for better support across platforms
    fmt.setProfile(QSurfaceFormat.CompatibilityProfile)
    
    # Set as default format for all OpenGL surfaces
    QSurfaceFormat.setDefaultFormat(fmt)


def run():
    """Run the Live2D desktop pet application"""
    # Configure OpenGL
    configure_opengl()

    # Set application attributes
    QCoreApplication.setAttribute(Qt.AA_UseDesktopOpenGL)  # Force desktop OpenGL
    QCoreApplication.setAttribute(Qt.AA_MacPluginApplication, True)  # Acts more like a plugin on macOS
    
    # Initialize Live2D
    live2d.init()
    
    app = None
    pet = None
    
    try:
        # Create application
        app = Application(sys.argv)
        
        # Create and show pet widget
        pet = PetWidget()
        app.register_pet_widget(pet)
        pet.show()
        
        # Run application
        return app.exec_()
    except Exception as e:
        print(f"Error running application: {e}")
        return 1
    finally:
        # Ensure proper cleanup order
        if pet:
            pet.cleanup()
        # Clean up Live2D resources only after other components are cleaned up
        live2d.dispose()


if __name__ == '__main__':
    sys.exit(run()) 