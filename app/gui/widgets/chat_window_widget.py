from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QScrollArea, QSizePolicy, QSpacerItem)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QEvent, QTimer
from PyQt5.QtGui import QFont, QIcon

from app.api.client import ApiClient
from app.gui.live2d.pet_widget import PetWidget
from app.api.chat_ws_client import ChatWebSocketClient
from app.api.endpoints import ApiRoutes

class ChatWindowWidget(QWidget):
    """
    A chat window widget that displays messages in bubbles and provides an input area.
    Styled to have a modern chat appearance.
    """
    send_message_signal = pyqtSignal(str) 
    # microphone_clicked_signal = pyqtSignal() # Microphone button removed from this widget

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ChatWindowWidget")

        # For dynamic input height, similar to ChatWidget
        self.input_padding = 16 # 8px top + 8px bottom (adjust if CSS padding changes)
        self.one_line_input_height = 0
        self.three_lines_input_height = 0 # Max height for 3 lines
        
        # Chat WebSocket client - optional, can be provided by parent
        self.chat_ws_client = None
        self.setup_websocket()

        self._init_ui()
        # Defer height calculation and initial adjustment until the event loop starts
        QTimer.singleShot(0, self._perform_initial_height_setup)

    def setup_websocket(self):
        """Set up the WebSocket client for chat"""
        self.chat_ws_client = ChatWebSocketClient(self)
        self.chat_ws_client.message_received.connect(self.on_message_received)
        self.chat_ws_client.connected.connect(self.on_ws_connected)
        self.chat_ws_client.disconnected.connect(self.on_ws_disconnected)
        self.chat_ws_client.error.connect(self.on_ws_error)
        
        # Connect to WebSocket
        QTimer.singleShot(500, self.connect_to_chat_websocket)
    
    def connect_to_chat_websocket(self):
        """Connect to the chat WebSocket server"""
        try:
            # Use ApiRoutes to get the WebSocket URL
            base_url = ApiClient.base_url
            if not base_url:
                base_url = "https://api.xbuddy.me/dev/api/v1"
                
            api_routes = ApiRoutes(base_url)
            ws_url = api_routes.chat_ws()
            
            self.chat_ws_client.connect_to_server(ws_url)
            print(f"Connecting to chat WebSocket at: {ws_url}")
        except Exception as e:
            print(f"Error connecting to chat WebSocket: {e}")
            try:
                fallback_url = "wss://api.xbuddy.me/dev/api/v1/chat/ws"
                print(f"Trying fallback chat WebSocket URL: {fallback_url}")
                self.chat_ws_client.connect_to_server(fallback_url)
            except Exception as fallback_e:
                print(f"Fallback chat connection also failed: {fallback_e}")
    
    def on_ws_connected(self):
        """Handle successful WebSocket connection"""
        print("Chat window connected to chat WebSocket server")
    
    def on_ws_disconnected(self):
        """Handle WebSocket disconnection"""
        print("Chat window disconnected from chat WebSocket server")
    
    def on_ws_error(self, error_message):
        """Handle WebSocket error"""
        print(f"Chat window WebSocket error: {error_message}")
        
    def on_message_received(self, message, code):
        """Handle received message from WebSocket"""
        if code == 0:
            self.receive_bot_message(message)
        elif code == 1: 
            self.receive_bot_message(f"Error: {message}")
        elif code == 2:  
            pass  
        else:
            print(f"Unknown message code: {code}")
            
    def set_chat_ws_client(self, ws_client):
        """Set the WebSocket client from an external source (e.g. parent widget)"""
        self.chat_ws_client = ws_client

    def _perform_initial_height_setup(self):
        """Calculates and applies the initial height for the message input field."""
        self._calculate_input_heights()
        self._adjust_input_height() # This will set it to one_line_input_height if empty

    def _init_ui(self):
        # 1. New Top-Level QHBoxLayout for the entire ChatWindowWidget
        top_level_h_layout = QHBoxLayout(self)
        # Apply overall margins from your latest settings
        top_level_h_layout.setContentsMargins(20, 10, 20, 20) 
        top_level_h_layout.setSpacing(10) # Spacing between chat area and photo area

        # 2. Create a container widget for the chat UI (messages + input bar)
        chat_ui_container = QWidget()
        chat_ui_container.setObjectName("ChatUIContainer")
        # This QVBoxLayout will manage the message area and input bar
        chat_v_layout = QVBoxLayout(chat_ui_container)
        chat_v_layout.setContentsMargins(0, 0, 0, 0) # No internal margins for this container
        chat_v_layout.setSpacing(10) # Spacing between message area and input bar

        # --- Existing Message Display Area setup --- 
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("MessageScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.message_container_widget = QWidget()
        self.message_container_widget.setObjectName("MessageContainerWidget")
        self.message_layout = QVBoxLayout(self.message_container_widget)
        self.message_layout.setContentsMargins(0, 0, 0, 0) # Let bubbles handle their own margins
        self.message_layout.setSpacing(30) # Increased spacing between bubbles to 20
        self.message_layout.addStretch(1)

        self.scroll_area.setWidget(self.message_container_widget)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        chat_v_layout.addWidget(self.scroll_area, 1) 

        # --- Existing Input Bar setup --- 
        self.input_bar = QWidget() 
        self.input_bar.setObjectName("InputBar")
        input_bar_layout = QHBoxLayout(self.input_bar)
        # Margins and spacing for content inside the input bar container
        input_bar_layout.setContentsMargins(4, 4, 4, 4) 
        input_bar_layout.setSpacing(5) 

        self.message_input = QTextEdit()
        self.message_input.setObjectName("MessageInput")
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setFont(QFont("Arial")) # Slightly larger font for input
        self.message_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.message_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # Managed by dynamic height
        self.message_input.setAcceptRichText(False)
        self.message_input.textChanged.connect(self._adjust_input_height)
        self.message_input.installEventFilter(self)

        self.send_button = QPushButton()
        self.send_button.setObjectName("SendButton")
        self.send_button.setIcon(QIcon("resources/icons/send-black-icon.png")) 
        self.send_button.setIconSize(QSize(20, 20))
        self.send_button.clicked.connect(self._on_send_message)

        input_bar_layout.addWidget(self.message_input)
        input_bar_layout.addWidget(self.send_button)
        
        chat_v_layout.addWidget(self.input_bar)

        # 3. Add the chat_ui_container to the left of top_level_h_layout
        top_level_h_layout.addWidget(chat_ui_container, 2) # Chat area takes 2/3 of space


        self._apply_styles() # General styles for ChatWindowWidget and its children

        # 4. Create the Photo Component (Placeholder for an image/custom widget)
        # TODO: Replace with Pet Widget
        self.pet_area = QLabel()
        
        # 5. Add the pet_area to the right of top_level_h_layout
        top_level_h_layout.addWidget(self.pet_area, 1) # Photo area takes 1/3 of space


    def _calculate_input_heights(self):
        font_metrics = self.message_input.fontMetrics()
        text_line_height = font_metrics.height()
        # self.input_padding is based on visual padding of the container + QTextEdit internal padding
        # If QTextEdit has its own CSS padding, that needs to be accounted for.
        # The following assumes self.input_padding is for the QTextEdit widget itself.
        self.one_line_input_height = text_line_height + self.input_padding
        # Estimate for 3 lines, accounting for some line spacing if any
        self.three_lines_input_height = (text_line_height * 3) + self.input_padding + (2 * 5) # 5px per inter-line spacing

    def _adjust_input_height(self):
        if not self.one_line_input_height: # Not calculated yet
            return
        doc_height = self.message_input.document().size().toSize().height()
        target_widget_height = doc_height + self.input_padding
        
        clamped_height = max(self.one_line_input_height, min(target_widget_height, self.three_lines_input_height))
        clamped_height = int(clamped_height)
        if self.message_input.height() != clamped_height:
            self.message_input.setFixedHeight(clamped_height)

    def _apply_styles(self):
        self.setStyleSheet("""
            #ChatWindowWidget {
                background-color: #ffffff; 
            }
            #MessageScrollArea {
                border: none;
                background-color: #ffffff;
            }
            #MessageContainerWidget {
                background-color: #ffffff;
            }
            /* Input bar container styling - like ChatWidget */
            #InputBar {
                background-color: rgba(240, 240, 240, 0.95); /* Light gray, slightly transparent */
                border-radius: 20px; /* Rounded container */
                padding: 2px; /* Minimal padding for the container itself */
                /*border-top: 1px solid #e0e0e0; /* Optional top border */
            }
            /* Message input field styling - like ChatWidget */
            #MessageInput {
                background-color: transparent; /* Transparent inside the #InputBar */
                color: #222222; /* Dark text */
                border: none; /* No border for the QTextEdit itself */
                padding: 8px 10px; /* Internal padding for text */
                font-size: 14px;
            }
            #SendButton {
                background-color: transparent;
                border: none;
                min-width: 28px; /* Consistent with setFixedSize */
                max-width: 28px;
                min-height: 28px;
                max-height: 28px;
                border-radius: 14px; /* Make it circular */
                margin-right: 4px; /* Some space from the edge of InputBar */
            }
            #SendButton:hover {
                background-color: rgba(0, 0, 0, 0.05); /* Subtle hover */
            }
            #SendButton:pressed {
                background-color: rgba(0, 0, 0, 0.1); /* Subtle press */
            }
            /* Ensure PhotoArea has a white background like the chat area */
            #PhotoArea {
                background-color: #ffffff; /* White background */
                /* border: 1px solid #e0e0e0; */ /* Optional: if you want a faint border */
            }
        """)

    def _create_message_bubble(self, text, is_user_message):
        bubble_container = QWidget()
        bubble_layout = QHBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0,0,0,0)
        bubble_layout.setSpacing(0)

        message_label = QLabel(text)
        message_label.setFont(QFont("Arial")) # Increased font size to 11pt
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred) # Allow width to expand
        message_label.setOpenExternalLinks(True) # Allow links to be clickable

        # Max width for the label itself, within the bubble_container
        # The bubble_container is pushed left/right by stretchers.
        # Removing setMaximumWidth in favor of layout stretch factors for more dynamic width
        # message_label.setMaximumWidth(int(self.scroll_area.width() * 0.92))

        bubble_base_style = """
            padding: 12px;
            border-radius: 10px;
            font-size: 13px;
        """

        if is_user_message:
            # User message (left, light gray background)
            message_label.setStyleSheet(f"""
                background-color: #E9E9EB; 
                color: #222222;
                {bubble_base_style}
            """)
            # User message: Label first, then spacer. Label gets stretch factor 5, spacer 5.
            bubble_layout.addWidget(message_label, 5) # Stretch factor for label (5 parts)
            bubble_layout.addStretch(5)               # Stretch factor for spacer (5 parts)
        else:
            # Bot/Other message (right, orange background as per image)
            message_label.setStyleSheet(f"""
                background-color: #FFE0B2; 
                color: #402C16;
                {bubble_base_style}
            """)
            # Bot message: Spacer first, then label. Label gets stretch factor 5, spacer 5.
            bubble_layout.addStretch(5)               # Stretch factor for spacer (5 parts)
            bubble_layout.addWidget(message_label, 5) # Stretch factor for label (5 parts)
        
        return bubble_container

    def add_message(self, text, is_user_message):
        if not text.strip():
            return

        if self.message_layout.count() > 0:
            item = self.message_layout.itemAt(self.message_layout.count() - 1)
            if item and item.spacerItem(): # Check if it'''s a spacer
                self.message_layout.takeAt(self.message_layout.count() -1) # Remove spacer

        bubble = self._create_message_bubble(text, is_user_message)
        self.message_layout.addWidget(bubble)
        self.message_layout.addStretch(1) # Add spacer back at the end

        QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )) # Delay slightly more for layout to settle

    def _on_send_message(self):
        message_text = self.message_input.toPlainText().strip()
        if message_text:
            self.add_message(message_text, True)
            self.send_message_signal.emit(message_text)
            
            # Send message via WebSocket if available
            if self.chat_ws_client and self.chat_ws_client.is_connected:
                # Detect language of message
                lang = self.detect_language(message_text)
                self.chat_ws_client.send_message(message_text, lang)
            
            self.message_input.clear()
            self._adjust_input_height() # Reset to one line height after send if empty

    def detect_language(self, text):
        """Detect if text is primarily Chinese or English"""
        # Simple check for Chinese characters
        chinese_chars = 0
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                chinese_chars += 1
                
        # If more than 20% of characters are Chinese, consider it Chinese
        if chinese_chars > 0 and chinese_chars / len(text) > 0.2:
            return "zh"
        return "en"

    def eventFilter(self, obj, event):
        if obj is self.message_input and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                if event.modifiers() & Qt.ShiftModifier:
                    return super().eventFilter(obj, event)
                else:
                    self._on_send_message()
                    return True 
        return super().eventFilter(obj, event)

    def receive_bot_message(self, text):
        self.add_message(text, False)
