import sys
from pathlib import Path
import OpenGL.GL as gl  # Make sure gl is imported at the module level
from OpenGL.GL import glGetString, GL_VERSION, GL_SHADING_LANGUAGE_VERSION, GL_VENDOR, GL_RENDERER
from PyQt5.QtGui import QMouseEvent, QKeyEvent, QCursor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

import live2d.v3 as live2d
from live2d.utils import log
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QOpenGLWidget, QApplication
from live2d.utils.lipsync import WavHandler
from live2d.v3 import StandardParams


# Use our SimpleCanvas implementation
from app.gui.widgets.simple_canvas import SimpleCanvas as Canvas
print("Using integrated SimpleCanvas")

live2d.setLogEnable(True)
RESOURCES_DIRECTORY = Path(__file__).parent.parent.parent.parent.absolute() / 'resources'


class BaseLive2D(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.model: None | live2d.LAppModel = None

        # Tool for controlling model opacity
        self.canvas: None | Canvas = None

        self.model_path: str = str(RESOURCES_DIRECTORY / "models/Haru/Haru.model3.json")

        self.setWindowTitle("Live2DCanvas")
        
        # Configure window for transparency and no shadows
        self.setWindowFlags(
            Qt.FramelessWindowHint |      # Borderless window
            Qt.WindowStaysOnTopHint |     # Always on top
            Qt.Tool |                     # Do not show in taskbar
            Qt.NoDropShadowWindowHint     # No shadow
        )
        
        # Enable transparent background
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Remove background
        self.setStyleSheet("background: transparent;")
        
        # Set initial size
        self.resize(300, 600)

    def initializeGL(self):
        super().initializeGL()
        # Print detailed OpenGL information for debugging
        print("GL_VERSION:", glGetString(GL_VERSION).decode())
        try:
            print("GLSL_VERSION:", glGetString(GL_SHADING_LANGUAGE_VERSION).decode())
            print("GL_VENDOR:", glGetString(GL_VENDOR).decode())
            print("GL_RENDERER:", glGetString(GL_RENDERER).decode())
        except Exception as e:
            print("Error getting additional OpenGL info:", str(e))
        
        # Initialize Live2D model
        try:
            live2d.glInit()  # Use glInit instead of glewInit
        except Exception as e:
            print("Warning: glInit failed, trying glewInit:", str(e))
            live2d.glewInit()
            
        self.model = live2d.LAppModel()
        self.model.LoadModelJson(self.model_path)

        # Try to create Canvas, handle possible errors
        self.canvas = Canvas()
        print("Canvas created successfully")

        # Print all available parameters
        for i in range(self.model.GetParameterCount()):
            param = self.model.GetParameter(i)
            log.Debug(
                param.id, param.type, param.value, param.max, param.min, param.default
            )

        self.startTimer(int(1000 / 60))

    def timerEvent(self, a0):
        super().timerEvent(a0)
        self.update()

    def on_draw(self):
        try:
            live2d.clearBuffer()
            self.model.Draw()
        except Exception as e:
            print(f"Error in on_draw: {str(e)}")

    def paintGL(self):
        try:
            # Clear with transparency
            gl.glClearColor(0.0, 0.0, 0.0, 0.0)  # Fully transparent background
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            
            # Set up alpha blending for proper transparency
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
            
            super().paintGL()
            self.model.Update()
            self.canvas.Draw(self.on_draw)
            
            # Restore OpenGL state
            gl.glDisable(gl.GL_BLEND)
        except Exception as e:
            print(f"Error in paintGL: {str(e)}")

    def resizeGL(self, width: int, height: int):
        try:
            super().resizeGL(width, height)
            self.model.Resize(width, height)
            self.canvas.SetSize(width, height)
        except Exception as e:
            print(f"Error in resizeGL: {str(e)}")


class MoveLive2D(BaseLive2D):
    def __init__(self):
        super().__init__()
        # Hold left mouse button to drag model
        self.dragging = False

    def isInModelArea(self, x: int, y: int) -> bool:
        try:
            h = self.height()
            px = int(x)
            py = int((h - y))
            data = gl.glReadPixels(px, py, 1, 1, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)
            alpha = data[3]
            result = alpha > 0
            return result
        except Exception as e:
            print(f"Error in isInModelArea: {str(e)}")
            return True  # Default to True if there's an error

    def mousePressEvent(self, a0: QMouseEvent):
        try:
            super().mousePressEvent(a0)
            x, y = a0.x(), a0.y()
            print(f'Pressed {x}, {y}')
            if self.isInModelArea(x, y):
                self.dragging = True
                self.drag_offset = a0.globalPos() - self.pos()
        except Exception as e:
            print(f"Error in mousePressEvent: {str(e)}")

    def mouseMoveEvent(self, a0: QMouseEvent):
        try:
            super().mouseMoveEvent(a0)
            x, y = a0.x(), a0.y()
            print(f'Moved {x}, {y}')
            if self.dragging:
                self.move(a0.globalPos() - self.drag_offset)
        except Exception as e:
            print(f"Error in mouseMoveEvent: {str(e)}")

    def mouseReleaseEvent(self, a0: QMouseEvent):
        try:
            super().mouseReleaseEvent(a0)
            x, y = a0.x(), a0.y()
            print(f'Released {x}, {y}')
            if self.dragging:
                self.dragging = False
        except Exception as e:
            print(f"Error in mouseReleaseEvent: {str(e)}")


class MotionLive2D(MoveLive2D):
    def __init__(self):
        super().__init__()
        self.dx: float = 0.0
        self.dy: float = 0.0

        self.fc = None
        self.sc = None

    def initializeGL(self):
        super().initializeGL()
        # self.model.StartRandomMotion("TapBody", 300, self.sc, self.fc)

        print("canvas size:", self.model.GetCanvasSize())
        print("canvas size in pixels:", self.model.GetCanvasSizePixel())
        print("pixels per unit:", self.model.GetPixelsPerUnit())

    def follow_mouse(self):
        global_pos = QCursor.pos()  # Get global mouse position
        local_pos = self.mapFromGlobal(global_pos)  # Convert to widget coordinates
        self.model.Drag(local_pos.x(), local_pos.y())

    def timerEvent(self, a0):
        self.model.SetOffset(self.dx, self.dy)
        self.follow_mouse()
        super().timerEvent(a0)

    def keyPressEvent(self, a0: QKeyEvent):
        super().keyPressEvent(a0)
        if a0.key() == Qt.Key_Left:
            self.dx -= 0.1
        elif a0.key() == Qt.Key_Right:
            self.dx += 0.1
        elif a0.key() == Qt.Key_Up:
            self.dy += 0.1
        elif a0.key() == Qt.Key_Down:
            self.dy -= 0.1
        elif a0.key() == Qt.Key_R:
            self.model.StopAllMotions()
            self.model.ResetPose()
        elif a0.key() == Qt.Key_E:
            self.model.ResetExpression()

    def on_start_motion_callback(self, group: str, no: int):
        log.Info("start motion: [%s_%d]" % (group, no))

    def on_finish_motion_callback(self):
        log.Info("motion finished")

    def mousePressEvent(self, a0: QMouseEvent):
        super().mousePressEvent(a0)
        self.model.SetRandomExpression()
        self.model.StartRandomMotion(
            priority=3,
            onStartMotionHandler=self.on_start_motion_callback,
            onFinishMotionHandler=self.on_finish_motion_callback)


class LipLive2D(MotionLive2D):
    def __init__(self):
        super().__init__()

        self.player = QMediaPlayer()
        self.wavHandler = WavHandler()
        self.lipSyncN = 3
        self.audioPlayed = False

    def play_audio(self, file_path: str):
        url = QUrl.fromLocalFile(file_path)
        media = QMediaContent(url)
        self.player.setMedia(media)
        self.player.play()

    def on_start_motion_callback(self, group: str, no: int):
        super().on_start_motion_callback(group, no)
        audio_path = str(RESOURCES_DIRECTORY / 'sounds/audio.wav')
        self.play_audio(audio_path)
        log.Info("start lipSync")
        self.wavHandler.Start(audio_path)

    def timerEvent(self, a0):
        if self.wavHandler.Update():
            # Update mouth opening and closing using wav loudness
            self.model.SetParameterValue(
                StandardParams.ParamMouthOpenY,
                self.wavHandler.GetRms() * self.lipSyncN
            )
        super().timerEvent(a0)


class PetWidget(LipLive2D):
    pass


def run(window_class: type):
    live2d.init()
    app = QApplication(sys.argv)
    win = window_class()
    win.show()
    app.exec()
    live2d.dispose()


if __name__ == '__main__':
    run(PetWidget)
