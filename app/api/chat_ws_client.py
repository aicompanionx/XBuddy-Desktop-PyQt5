import json
import time
import os
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWebSockets import QWebSocket
from PyQt5.QtCore import QUrl

class ChatWebSocketClientBase(QObject):
    """Base WebSocket client for chat communication - Abstract base class"""
    
    # Signal emitted when receiving chat message parts
    message_received = pyqtSignal(str, int)  # message, code
    
    # Signal for connection status changes
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ws_url = ""
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
    
    def connect_to_server(self, url):
        """Connect to the chat WebSocket server"""
        raise NotImplementedError("Subclasses must implement this")
    
    def reconnect(self):
        """Attempt to reconnect to the WebSocket server"""
        raise NotImplementedError("Subclasses must implement this")
    
    def disconnect_from_server(self):
        """Disconnect from the chat WebSocket server"""
        raise NotImplementedError("Subclasses must implement this")
    
    def send_message(self, message, lang="en"):
        """Send a chat message"""
        raise NotImplementedError("Subclasses must implement this")


class RealChatWebSocketClient(ChatWebSocketClientBase):
    """Real WebSocket client implementation for chat communication"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create WebSocket client - 不使用VersionLatest属性，它不存在
        self.ws_client = QWebSocket("", QWebSocket.Default, self)
        
        # Connect signals
        self.ws_client.connected.connect(self._on_connected)
        self.ws_client.disconnected.connect(self._on_disconnected)
        self.ws_client.textMessageReceived.connect(self._on_message_received)
        self.ws_client.error.connect(lambda error_code: self._on_error(f"WebSocket error: {error_code}"))
        
        # Reconnect timer
        self.reconnect_timer = QTimer(self)
        self.reconnect_timer.timeout.connect(self.reconnect)
        self.reconnect_timer.setInterval(5000)  # 5 seconds between reconnections
    
    def connect_to_server(self, url):
        """Connect to the chat WebSocket server"""
        print(f"Connecting to chat WebSocket at: {url}")
        self.ws_url = url
        self.reconnect_attempts = 0
        self.ws_client.open(QUrl(url))
    
    def reconnect(self):
        """Attempt to reconnect to the WebSocket server"""
        if self.is_connected or self.reconnect_attempts >= self.max_reconnect_attempts:
            self.reconnect_timer.stop()
            return
            
        print(f"Reconnecting to chat WebSocket (Attempt {self.reconnect_attempts + 1})")
        self.reconnect_attempts += 1
        self.connect_to_server(self.ws_url)
    
    def disconnect_from_server(self):
        """Disconnect from the chat WebSocket server"""
        print("Disconnecting from chat WebSocket")
        self.ws_client.close()
        self.is_connected = False
        self.reconnect_timer.stop()
    
    def send_message(self, message, lang="en"):
        """Send a chat message"""
        if not self.is_connected:
            self.error.emit("Cannot send message: Not connected to server")
            return False
        
        try:
            # Construct message according to API format
            payload = {
                "data": {
                    "content": message,
                    "lang": lang
                },
                "type": "chat"
            }
            
            # Send as JSON
            self.ws_client.sendTextMessage(json.dumps(payload))
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            self.error.emit(f"Error sending message: {e}")
            return False
    
    def _on_connected(self):
        """Handle successful WebSocket connection"""
        print("Chat WebSocket connected")
        self.is_connected = True
        self.reconnect_attempts = 0
        self.reconnect_timer.stop()
        self.connected.emit()
    
    def _on_disconnected(self):
        """Handle WebSocket disconnection"""
        print("Chat WebSocket disconnected")
        self.is_connected = False
        self.disconnected.emit()
        
        # Start reconnection timer if not manually disconnected
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_timer.start()
    
    def _on_error(self, error_message):
        """Handle WebSocket error"""
        print(f"Chat WebSocket error: {error_message}")
        self.error.emit(error_message)
    
    def _on_message_received(self, message):
        """Handle received chat message"""
        try:
            # Parse JSON message
            data = json.loads(message)
            
            # Check if it's a chat message
            if data.get("type") == "chat":
                chat_data = data.get("data", {})
                message_text = chat_data.get("message", "")
                message_code = chat_data.get("code", 1)  # Default to error code 1 if not present
                
                # Emit signal with message and code
                self.message_received.emit(message_text, message_code)
            else:
                print(f"Received non-chat message: {data}")
        except json.JSONDecodeError:
            print(f"Received invalid JSON: {message}")
            self.error.emit(f"Received invalid JSON from server")
        except Exception as e:
            print(f"Error processing message: {e}")
            self.error.emit(f"Error processing message: {e}")


class MockChatWebSocketClient(ChatWebSocketClientBase):
    """Simulated WebSocket client for chat communication"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Timer for simulating response delays
        self.response_timer = QTimer(self)
        self.response_timer.setSingleShot(True)
        self.response_timer.timeout.connect(self._simulate_response)
        
        # Reconnect timer for handling disconnections
        self.reconnect_timer = QTimer(self)
        self.reconnect_timer.timeout.connect(self.reconnect)
        self.reconnect_timer.setInterval(5000)  # 5 seconds between reconnection attempts
        
        self.current_message = ""
    
    def connect_to_server(self, url):
        """Connect to the chat WebSocket server"""
        print(f"Simulating connection to chat WebSocket at: {url}")
        self.ws_url = url
        self.reconnect_attempts = 0
        
        # Simulate connection delay
        QTimer.singleShot(500, self._on_connected)
    
    def reconnect(self):
        """Attempt to reconnect to the WebSocket server"""
        if self.is_connected or self.reconnect_attempts >= self.max_reconnect_attempts:
            self.reconnect_timer.stop()
            return
            
        print(f"Simulating reconnection to chat WebSocket (Attempt {self.reconnect_attempts + 1})")
        self.reconnect_attempts += 1
        self.connect_to_server(self.ws_url)
    
    def disconnect_from_server(self):
        """Disconnect from the chat WebSocket server"""
        print("Disconnecting from simulated chat WebSocket")
        self.is_connected = False
        self.response_timer.stop()
        self.reconnect_timer.stop()
        self.disconnected.emit()
    
    def send_message(self, message, lang="en"):
        """Send a chat message"""
        if not self.is_connected:
            self.error.emit("Cannot send message: Not connected to server")
            return False
        
        try:
            # Store the message for simulation
            self.current_message = message
            
            # Log the message format that would be sent
            payload = {
                "data": {
                    "content": message,
                    "lang": lang
                },
                "type": "chat"
            }
            print(f"Simulating sending chat message: {json.dumps(payload)}")
            
            # Simulate network delay (200-800ms)
            response_delay = 200 + (len(message) * 5)  # Longer messages take more time
            response_delay = min(response_delay, 800)  # Cap at 800ms
            self.response_timer.start(response_delay)
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            self.error.emit(f"Error sending message: {e}")
            return False
    
    def _on_connected(self):
        """Handle successful WebSocket connection"""
        print("Simulated Chat WebSocket connected")
        self.is_connected = True
        self.reconnect_attempts = 0
        self.reconnect_timer.stop()
        self.connected.emit()
    
    def _on_error(self, error_message):
        """Handle WebSocket error"""
        print(f"Simulated Chat WebSocket error: {error_message}")
        self.error.emit(error_message)
    
    def _simulate_response(self):
        """Simulate receiving a message response"""
        if not self.is_connected:
            return
            
        # Create a simple response based on the current message
        message = self.current_message.lower()
        
        try:
            # Simulate streaming response with multiple chunks
            if len(message) > 10:
                # First stream some content
                self._emit_message_chunk("I'm processing your request about: " + message[:10] + "...", 0)
                
                # Schedule the next chunk
                QTimer.singleShot(500, lambda: self._stream_next_chunk(message, 1))
            else:
                # Short response in one go
                response = f"You said: {message}. This is a simulated response."
                self._emit_message_chunk(response, 0)
                
                # Send the completion signal after a delay
                QTimer.singleShot(300, lambda: self.message_received.emit("", 2))
        except Exception as e:
            print(f"Error simulating response: {e}")
            self.error.emit(f"Error simulating response: {e}")
    
    def _stream_next_chunk(self, message, chunk_num):
        """Send the next chunk of a streaming response"""
        if not self.is_connected:
            return
            
        if chunk_num == 1:
            # Second chunk
            response = f"Here's what I found about {message}: This is a simulated API response."
            self._emit_message_chunk(response, 0)
            
            # Schedule final chunk
            QTimer.singleShot(700, lambda: self._stream_next_chunk(message, 2))
        elif chunk_num == 2:
            # Final chunk
            self._emit_message_chunk(" Is there anything else you'd like to know?", 0)
            
            # Send completion signal
            QTimer.singleShot(200, lambda: self.message_received.emit("", 2))
    
    def _emit_message_chunk(self, text, code):
        """Emit a message chunk with the specified code"""
        self.message_received.emit(text, code)


def ChatWebSocketClient(parent=None):
    """Factory function to create the appropriate ChatWebSocketClient based on environment or config"""
    use_real = os.environ.get("USE_REAL_CHAT_WS", "").lower() in ("true", "1", "yes")
    
    # You could also check a config variable or any other logic here
    # if some_config.get("use_real_websocket"):
    #    use_real = True
    
    if use_real:
        try:
            print("Using real chat WebSocket client")
            return RealChatWebSocketClient(parent)
        except Exception as e:
            print(f"Error creating real WebSocket client, falling back to mock: {e}")
            return MockChatWebSocketClient(parent)
    else:
        print("Using simulated chat WebSocket client")
        return MockChatWebSocketClient(parent) 