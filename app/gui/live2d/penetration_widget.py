from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QThread, QElapsedTimer, QRect
from PyQt5.QtGui import QBitmap, QRegion, QImage

from app.gui.live2d.base_widget import BaseLive2DWidget


# Worker class for generating a mask in a separate thread
class MaskGeneratorWorker(QObject):
    maskReady = pyqtSignal(QRegion)
    finished = pyqtSignal()  # Signal to indicate processing is done

    def __init__(self):
        super().__init__()
        self._image_to_process = None

    @pyqtSlot(QImage)
    def processImage(self, image: QImage):
        expanded_region = QRegion()  # Region to store the expanded mask
        expansion_pixels = 50        # Number of pixels to expand outward

        if not image.isNull() and image.hasAlphaChannel():
            # Use ThresholdAlphaDither flag for smoother edges
            mask_mono_image = image.createAlphaMask(Qt.ThresholdAlphaDither)
            if not mask_mono_image.isNull():
                mask_bitmap = QBitmap.fromImage(mask_mono_image)
                original_region = QRegion(mask_bitmap)

                if not original_region.isEmpty():
                    # Iterate over all rectangles in the original region
                    for rect in original_region.rects():
                        # Expand each rectangle
                        # adjusted(dx1, dy1, dx2, dy2) adjusts left, top, right, bottom edges
                        # Negative values expand outward, positive shrink inward
                        expanded_rect = rect.adjusted(-expansion_pixels, -expansion_pixels, expansion_pixels, expansion_pixels)
                        # Merge the expanded rectangle into the final region
                        expanded_region = expanded_region.united(QRegion(expanded_rect))

                    # (Optional) Clip the final region within image bounds
                    # image_bounds_rect = QRect(0, 0, image.width(), image.height())
                    # expanded_region = expanded_region.intersected(QRegion(image_bounds_rect))

                    self.maskReady.emit(expanded_region)
                else:
                    # Emit empty region if the original is empty
                    self.maskReady.emit(QRegion())
            else:
                # Failed to create alpha mask image
                self.maskReady.emit(QRegion())
        else:
            # Invalid image or no alpha channel
            self.maskReady.emit(QRegion())
        self.finished.emit()


class PenetrationLive2DWidget(BaseLive2DWidget):
    # Signal to request mask update in the worker thread
    requestMaskUpdate = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()

        # Setup worker thread for mask generation
        self.mask_worker = MaskGeneratorWorker()
        self.mask_thread = QThread()
        self.mask_worker.moveToThread(self.mask_thread)

        # Connect signals/slots
        self.requestMaskUpdate.connect(self.mask_worker.processImage)
        self.mask_worker.maskReady.connect(self.applyMaskSlot)
        self.mask_worker.finished.connect(self.onMaskProcessingFinished)

        self.mask_thread.start()
        self.mask_processing_busy = False
        self.current_mask_region = QRegion()  # Store the current mask
        self.mask_update_timer = QElapsedTimer()
        self.mask_update_interval_ms = 50  # Update mask every 50 ms (~20 FPS)
        self.mask_update_timer.start()

    @pyqtSlot(QRegion)
    def applyMaskSlot(self, region: QRegion):
        # Only update the mask if it's different from the current one
        if region != self.current_mask_region:
            if not region.isEmpty():
                self.setMask(region)
                self.current_mask_region = region
            else:
                # Clear the mask if the new region is empty and current one is not
                if not self.current_mask_region.isEmpty():
                    self.clearMask()
                    self.current_mask_region = QRegion()

    @pyqtSlot()
    def onMaskProcessingFinished(self):
        self.mask_processing_busy = False

    def paintGL(self):
        super().paintGL()
        # Check if enough time has passed and the worker is not busy
        if not self.mask_processing_busy and self.mask_update_timer.elapsed() > self.mask_update_interval_ms:
            image = self.grabFramebuffer()
            if not image.isNull() and image.hasAlphaChannel():
                self.mask_processing_busy = True
                # Send a copy of the image to the worker thread
                self.requestMaskUpdate.emit(image.copy())
                self.mask_update_timer.restart()
            elif image.isNull() or not image.hasAlphaChannel():
                # If the image is invalid, clear the mask if needed
                if not self.current_mask_region.isEmpty():
                    self.clearMask()
                    self.current_mask_region = QRegion()
                self.mask_processing_busy = False
                self.mask_update_timer.restart()
        # If busy or interval not met, mask won't update until next frame

    def __del__(self):  # Destructor to clean up the thread
        self.mask_thread.quit()
        self.mask_thread.wait()
