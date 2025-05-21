from live2d.utils.lipsync import WavHandler
from live2d.v3 import StandardParams
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

from xbuddy.gui.pet_widgets.motion_widget import MotionLive2DWidget
from xbuddy.gui.utils import get_logger, run
from xbuddy.settings import RESOURCES_DIRECTORY

logger = get_logger(__name__)


class LipSyncLive2DWidget(MotionLive2DWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.player = QMediaPlayer()
        self.wavHandler = WavHandler()
        self.lipSyncN = 3
        self.disable_play_sound = False

    def play_audio(self, file_path: str):
        url = QUrl.fromLocalFile(file_path)
        media = QMediaContent(url)
        self.player.setMedia(media)
        self.player.play()

    def on_start_motion_callback(self, group: str, no: int):
        super().on_start_motion_callback(group, no)
        if not self.disable_play_sound:
            audio_path = str(RESOURCES_DIRECTORY / "sounds/audio.wav")
            self.play_audio(audio_path)
            logger.info("start lipSync")
            self.wavHandler.Start(audio_path)

    def timerEvent(self, a0):
        if self.wavHandler.Update():
            self.model.SetParameterValue(
                StandardParams.ParamMouthOpenY, self.wavHandler.GetRms() * self.lipSyncN
            )
        super().timerEvent(a0)


if __name__ == "__main__":
    run(LipSyncLive2DWidget)
