"""
Live2D widget with lip synchronization for audio playback.
"""

from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from live2d.utils import log
from live2d.utils.lipsync import WavHandler
from live2d.v3 import StandardParams
from app.gui.live2d.animated_widget import AnimatedLive2DWidget
from app.gui.live2d.base_widget import RESOURCES_DIRECTORY


class LipSyncLive2DWidget(AnimatedLive2DWidget):
    """
    Live2D widget with lip synchronization capabilities.
    Adds support for:
    - Audio playback
    - Lip movement synchronized with audio
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize audio player
        self.player = QMediaPlayer()
        
        # Initialize lip sync handler
        self.wavHandler = WavHandler()
        
        # Lip sync sensitivity multiplier
        self.lipSyncN = 3
        
        # Audio playback state
        self.audioPlayed = False

    def play_audio(self, file_path):
        """
        Play audio file using QMediaPlayer.
        
        Args:
            file_path (str): Path to the audio file to play
        """
        # Convert file path to QUrl
        url = QUrl.fromLocalFile(file_path)
        
        # Create media content from URL
        media = QMediaContent(url)
        
        # Set and play the media
        self.player.setMedia(media)
        self.player.play()

    def on_start_motion_callback(self, group, no):
        """
        Extended callback when motion starts.
        Also starts audio playback and lip sync.
        """
        # Call parent implementation
        super().on_start_motion_callback(group, no)
        
        # Path to audio file
        audio_path = str(RESOURCES_DIRECTORY / 'sounds/audio.wav')
        
        # Play audio file
        self.play_audio(audio_path)
        
        # Start lip sync processing
        log.Info("Starting lip sync")
        self.wavHandler.Start(audio_path)

    def timerEvent(self, event):
        """
        Handle timer events for animation and lip sync.
        Updates mouth parameters based on audio amplitude.
        """
        # Update lip sync if active
        if self.wavHandler.Update():
            # Update mouth opening parameter based on audio volume
            self.model.SetParameterValue(
                StandardParams.ParamMouthOpenY,
                self.wavHandler.GetRms() * self.lipSyncN
            )
            
        # Call parent implementation
        super().timerEvent(event) 