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

        # Flag to control lip sync
        self.lip_sync_enabled = True
        self.play_sound_enabled = True

    def play_audio(self, file_path):
        """
        Play audio file using QMediaPlayer.
        
        Args:
            file_path (str): Path to the audio file to play
        """
        try:
            # Convert file path to QUrl
            url = QUrl.fromLocalFile(file_path)

            # Create media content from URL
            media = QMediaContent(url)

            # Set and play the media
            self.player.setMedia(media)
            self.player.play()
        except Exception as e:
            print(f"Error playing audio: {e}")

    def stop_audio(self):
        """Stop any playing audio and clean up resources."""
        try:
            if self.player:
                self.player.stop()
            if self.wavHandler:
                # Reset the lip sync handler
                self.lip_sync_enabled = False
        except Exception as e:
            print(f"Error stopping audio: {e}")

    def cleanup_lip_sync(self):
        """Clean up lip sync and audio resources."""
        self.stop_audio()
        self.lip_sync_enabled = False

        # Clear references
        try:
            if hasattr(self, 'player') and self.player:
                self.player.stop()
                self.player.setMedia(QMediaContent())  # Clear media

            # Set to None at the end to avoid access during cleanup
            self.wavHandler = None
            self.player = None
        except Exception as e:
            print(f"Error in cleanup_lip_sync: {e}")

    def on_start_motion_callback(self, group, no):
        """
        Extended callback when motion starts.
        Also starts audio playback and lip sync.
        """
        # Call parent implementation
        super().on_start_motion_callback(group, no)

        # Skip if lip sync is disabled
        if (not self.lip_sync_enabled or
                not self.play_sound_enabled or
                not self.wavHandler):
            return

        try:
            # Path to audio file
            audio_path = str(RESOURCES_DIRECTORY / 'sounds/audio.wav')

            # Play audio file
            self.play_audio(audio_path)

            # Start lip sync processing
            log.Info("Starting lip sync")
            self.wavHandler.Start(audio_path)
        except Exception as e:
            print(f"Error in start motion callback: {e}")
            self.lip_sync_enabled = False

    def timerEvent(self, event):
        """
        Handle timer events for animation and lip sync.
        Updates mouth parameters based on audio amplitude.
        """
        # Skip if lip sync is disabled or resources are missing
        if not self.lip_sync_enabled or not self.wavHandler or not self.model:
            return super().timerEvent(event)

        try:
            # Update lip sync if active
            if self.wavHandler.Update():
                # Update mouth opening parameter based on audio volume
                self.model.SetParameterValue(
                    StandardParams.ParamMouthOpenY,
                    self.wavHandler.GetRms() * self.lipSyncN
                )
        except Exception as e:
            print(f"Error in lip sync timerEvent: {e}")
            self.lip_sync_enabled = False

        # Call parent implementation
        try:
            super().timerEvent(event)
        except Exception as e:
            print(f"Error calling parent timerEvent: {e}")

    def stop_animations(self):
        """Override to also stop audio and lip sync."""
        super().stop_animations()
        self.stop_audio()
