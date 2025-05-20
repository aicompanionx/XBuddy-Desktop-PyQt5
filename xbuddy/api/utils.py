import asyncio
import traceback
from urllib.parse import urljoin

import websockets
from pydantic import BaseModel
from PyQt5.QtCore import QThread, pyqtSignal

from xbuddy.gui.utils import get_logger
from xbuddy.settings import API_SERVER

logger = get_logger(__name__)


class WebSocketWorker(QThread):
    RECONNECT_INTERVAL = 5
    message_received = pyqtSignal(str)

    def __init__(self, url: str, model: type[BaseModel]):
        super().__init__()
        base = f"ws://{API_SERVER}"
        self.url = urljoin(base, url)
        self.model = model
        self.running = True

    async def listen_once(self):
        try:
            async with websockets.connect(self.url, ping_interval=None) as ws:
                logger.info("WebSocket connected.")
                while self.running:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=60)
                        try:
                            message = self.model.model_validate_json(message)
                            self.message_received.emit(message.model_dump_json())
                        except Exception:
                            logger.error(
                                f"Message error: {traceback.format_exc()}\nMessage: {message}"
                            )
                    except TimeoutError:
                        logger.warning(
                            "WebSocket receive timeout. Trying to reconnect."
                        )
                        break
        except Exception:
            logger.error(f"WebSocket connection error: {traceback.format_exc()}")
            await asyncio.sleep(self.RECONNECT_INTERVAL)

    async def listen_loop(self):
        while self.running:
            await self.listen_once()
            if self.running:
                logger.info(
                    f"Retrying connection in {self.RECONNECT_INTERVAL} seconds..."
                )
                await asyncio.sleep(self.RECONNECT_INTERVAL)

    def run(self):
        asyncio.run(self.listen_loop())

    def stop(self):
        self.running = False
