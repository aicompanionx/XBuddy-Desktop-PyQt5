import os

import live2d.v3 as live2d
from live2d.v3.live2d import LAppModel
from PyQt5.QtWidgets import QOpenGLWidget

from xbuddy.gui.utils import get_logger, run, transparent
from xbuddy.settings import DEFAULT_MODEL_SCALE, FPS, RESOURCES_DIRECTORY

logger = get_logger(__name__)


class BaseLive2DWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.model: LAppModel | None = None

        self.model_list = self._find_model3_json_files(RESOURCES_DIRECTORY / "models")
        self.model_path = str(RESOURCES_DIRECTORY / "models/Haru/Haru.model3.json")

        transparent(self)
        self.resize(800, 800)

    def _find_model3_json_files(self, root_dir) -> list[str]:
        model_files = []
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith("model3.json"):
                    model_files.append(str(os.path.join(dirpath, filename)))
        return model_files

    def initializeGL(self):
        super().initializeGL()
        live2d.glewInit()
        self.model = live2d.LAppModel()
        self.model.LoadModelJson(self.model_path)
        self.model.SetScale(DEFAULT_MODEL_SCALE)
        self.startTimer(int(1000 / FPS))  # set fps

    def timerEvent(self, a0):
        super().timerEvent(a0)
        self.update()

    def paintGL(self):
        super().paintGL()
        self.model.Update()
        live2d.clearBuffer()
        self.model.Draw()

        self.mask_image = self.grabFramebuffer()

    def resizeGL(self, width: int, height: int):
        super().resizeGL(width, height)
        self.model.Resize(width, height)


if __name__ == "__main__":
    run(BaseLive2DWidget)
