import os
import sys
from pathlib import Path
import OpenGL.GL as gl
from PyQt5.QtGui import QMouseEvent, QKeyEvent, QCursor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from live2d.utils.canvas import Canvas
import live2d.v3 as live2d
from live2d.utils import log
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QOpenGLWidget, QApplication
from live2d.utils.lipsync import WavHandler
from live2d.v3 import StandardParams

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
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # Borderless window
            Qt.WindowStaysOnTopHint |  # Always on top (optional)
            Qt.Tool  # Do not show in taskbar
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # Enable transparent background
        self.resize(300, 600)

    def initializeGL(self):
        super().initializeGL()
        live2d.glewInit()
        self.model = live2d.LAppModel()
        self.model.LoadModelJson(self.model_path)

        # Must be created after OpenGL context is configured
        self.canvas = Canvas()

        # Disable auto-blink
        # self.model.SetAutoBlinkEnable(False)
        # Disable auto-breath
        # self.model.SetAutoBreathEnable(False)
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
        live2d.clearBuffer()
        self.model.Draw()

    def paintGL(self):
        super().paintGL()
        self.model.Update()
        self.canvas.Draw(self.on_draw)

    def resizeGL(self, width: int, height: int):
        super().resizeGL(width, height)
        self.model.Resize(width, height)
        self.canvas.SetSize(width, height)


class MoveLive2D(BaseLive2D):
    def __init__(self):
        super().__init__()
        # Hold left mouse button to drag model
        self.dragging = False

    def isInModelArea(self, x: int, y: int) -> bool:
        h = self.height()
        px = int(x)
        py = int((h - y))
        data = gl.glReadPixels(px, py, 1, 1, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)
        alpha = data[3]
        result = alpha > 0
        return result

    def mousePressEvent(self, a0: QMouseEvent):
        super().mousePressEvent(a0)
        x, y = a0.x(), a0.y()
        print(f'Pressed {x}, {y}')
        if self.isInModelArea(x, y):
            self.dragging = True
            self.drag_offset = a0.globalPos() - self.pos()

    def mouseMoveEvent(self, a0: QMouseEvent):
        super().mouseMoveEvent(a0)
        x, y = a0.x(), a0.y()
        print(f'Moved {x}, {y}')
        if self.dragging:
            self.move(a0.globalPos() - self.drag_offset)

    def mouseReleaseEvent(self, a0: QMouseEvent):
        super().mouseReleaseEvent(a0)
        x, y = a0.x(), a0.y()
        print(f'Released {x}, {y}')
        if self.dragging:
            self.dragging = False


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
