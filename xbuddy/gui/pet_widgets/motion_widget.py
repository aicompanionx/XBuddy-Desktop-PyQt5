import time

from PyQt5.QtGui import QCursor, QMouseEvent

from xbuddy.gui.pet_widgets.move_widget import MoveLive2DWidget
from xbuddy.gui.utils import get_logger, run

logger = get_logger(__name__)


class MotionLive2DWidget(MoveLive2DWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.motion_interval = 0.25
        self.motion_start = time.time()

    def follow_mouse(self):
        global_pos = QCursor.pos()
        local_pos = self.mapFromGlobal(global_pos)
        self.model.Drag(local_pos.x(), local_pos.y())

    def timerEvent(self, a0):
        self.follow_mouse()

        super().timerEvent(a0)

    def on_start_motion_callback(self, group: str, no: int):
        logger.info(f"start motion: [{group}_{no}]")

    def on_finish_motion_callback(self):
        logger.info("motion finished")

    def mousePressEvent(self, a0: QMouseEvent | None):
        super().mousePressEvent(a0)
        if time.time() - self.motion_start > self.motion_interval:
            self.motion_start = time.time()
            self.model.SetRandomExpression()
            self.model.StartRandomMotion(
                priority=3,
                onStartMotionHandler=self.on_start_motion_callback,
                onFinishMotionHandler=self.on_finish_motion_callback,
            )


if __name__ == "__main__":
    run(MotionLive2DWidget)
