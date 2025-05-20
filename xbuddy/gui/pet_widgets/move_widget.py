import OpenGL.GL as gl
from PyQt5.QtGui import QMouseEvent

from xbuddy.gui.pet_widgets.base_widget import BaseLive2DWidget
from xbuddy.gui.utils import get_logger, run

logger = get_logger(__name__)


class MoveLive2DWidget(BaseLive2DWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # hold left key to dray model
        self.dragging = False
        self.drag_offset = None

    def isInModelArea(self, x: int, y: int) -> bool:
        h = self.height()
        data = gl.glReadPixels(
            int(x), int(h - y), 1, 1, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE
        )
        alpha = data[3]
        result = alpha > 0
        return result

    def mousePressEvent(self, a0: QMouseEvent | None):
        super().mousePressEvent(a0)
        x, y = a0.x(), a0.y()
        if self.isInModelArea(x, y):
            self.dragging = True
            self.drag_offset = a0.globalPos() - self.window().frameGeometry().topLeft()

    def mouseMoveEvent(self, a0: QMouseEvent | None):
        super().mouseMoveEvent(a0)
        if self.dragging:
            self.window().move(a0.globalPos() - self.drag_offset)

    def mouseReleaseEvent(self, a0: QMouseEvent | None):
        super().mouseReleaseEvent(a0)
        if self.dragging:
            self.dragging = False


if __name__ == "__main__":
    run(MoveLive2DWidget)
