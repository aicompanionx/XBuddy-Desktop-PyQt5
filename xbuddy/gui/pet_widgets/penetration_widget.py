from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QBitmap, QImage, QRegion

from xbuddy.gui.pet_widgets.lip_sync_widget import LipSyncLive2DWidget
from xbuddy.gui.utils import get_logger, run

logger = get_logger(__name__)


class MaskGeneratorWorker(QObject):
    maskReady = pyqtSignal(QRegion)
    finished = pyqtSignal()  # Signal to indicate processing is done

    def __init__(self):
        super().__init__()
        self._image_to_process = None

    @pyqtSlot(QImage)
    def processImage(self, image: QImage):
        if not image.isNull() and image.hasAlphaChannel():
            # Use ThresholdAlphaDither flag for potentially smoother model edges
            mask_mono_image = image.createAlphaMask(Qt.ThresholdAlphaDither)
            if not mask_mono_image.isNull():
                mask_bitmap = QBitmap.fromImage(mask_mono_image)
                region = QRegion(mask_bitmap)
                self.maskReady.emit(region)
            else:
                # Emit an empty region or a specific signal if mask creation fails
                self.maskReady.emit(QRegion())
        else:
            # Emit an empty region if image is invalid
            self.maskReady.emit(QRegion())
        self.finished.emit()


class PenetrationLive2DWidget(LipSyncLive2DWidget):
    # Signal to request mask update in the worker thread
    requestMaskUpdate = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup worker thread for mask generation
        self.mask_worker = MaskGeneratorWorker()
        self.mask_thread = QThread()
        self.mask_worker.moveToThread(self.mask_thread)

        # Connect signals/slots
        self.requestMaskUpdate.connect(self.mask_worker.processImage)
        self.mask_worker.maskReady.connect(self.applyMaskSlot)
        self.mask_worker.finished.connect(
            self.onMaskProcessingFinished
        )  # Connect worker's finished signal

        self.mask_thread.start()
        self.mask_processing_busy = False

    @pyqtSlot(QRegion)
    def applyMaskSlot(self, region: QRegion):
        if not region.isEmpty():
            self.setMask(region)
        else:
            self.clearMask()  # Clear mask if region is empty (e.g. processing failed)
        # self.mask_processing_busy = False # Moved to onMaskProcessingFinished

    @pyqtSlot()
    def onMaskProcessingFinished(self):
        self.mask_processing_busy = False

    def paintGL(self):
        super().paintGL()
        if not self.mask_processing_busy:
            image = self.grabFramebuffer()
            if not image.isNull() and image.hasAlphaChannel():
                self.mask_processing_busy = True
                # Pass a copy of the image to the worker thread
                self.requestMaskUpdate.emit(image.copy())
            elif image.isNull() or not image.hasAlphaChannel():
                # If image is bad, clear mask immediately and ensure busy flag is false
                self.clearMask()
                self.mask_processing_busy = False
        # If busy, the current frame will not update the mask,
        # it will be updated when the worker finishes the previous request.

    def __del__(self):  # Destructor to clean up thread
        self.mask_thread.quit()
        self.mask_thread.wait()


if __name__ == "__main__":
    run(PenetrationLive2DWidget)
