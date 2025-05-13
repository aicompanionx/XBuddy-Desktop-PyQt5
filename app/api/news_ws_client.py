import json
import time
import random
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from app.model.news_model import NewsModel


class NewsWebSocketClient(QObject):
    """
    Mock WebSocket client for simulating news data
    This implementation uses a timer to simulate receiving news periodically
    """
    
    # Signal emitted when new news data is received
    news_received = pyqtSignal(NewsModel)
    
    # Signal for connection status changes
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Timer for simulating incoming news data
        self.news_timer = QTimer(self)
        self.news_timer.timeout.connect(self._simulate_news_message)
        
        # Reconnect timer for handling disconnections
        self.reconnect_timer = QTimer(self)
        self.reconnect_timer.timeout.connect(self.reconnect)
        self.reconnect_timer.setInterval(5000)  # 5 seconds between reconnection attempts
        
        self.ws_url = ""
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
        # Sample news data for simulation
        self.sample_news = [
            {
                "title": "Bitcoin Breaks $65,000, Market Sentiment Turns Optimistic",
                "abstract": "Bitcoin experienced a strong rally over the past 24 hours, surging by 5% and successfully breaking through the $65,000 mark. This significant upward movement has sparked renewed optimism among investors.",
                "cover_img": "https://example.com/bitcoin.jpg",
                "id": 100001,
                "news_url": "https://example.com/bitcoin-news",
                "origin_url": "https://example.com/bitcoin-news",
                "published_at": int(time.time()),
                "sort_id": 1,
                "source_id": "crypto_news_123",
                "source_name": "Crypto News",
                "source_type": 5,
                "type": 2
            },
            {
                "title": "Ethereum 2.0 Staking Reaches New All-Time High",
                "abstract": "The amount of ETH staked on the Ethereum network has reached an all-time high, indicating growing confidence in the upcoming network upgrade. More than 20 million ETH is now locked in staking contracts.",
                "cover_img": "https://example.com/ethereum.jpg",
                "id": 100002,
                "news_url": "https://example.com/ethereum-news",
                "origin_url": "https://example.com/ethereum-news",
                "published_at": int(time.time()),
                "sort_id": 1,
                "source_id": "eth_news_456",
                "source_name": "ETH Updates",
                "source_type": 5,
                "type": 2
            },
            {
                "title": "Major Exchange Introduces Support for New Payment Methods",
                "abstract": "Binance has announced the addition of several payment methods for users in Europe and Asia, expanding access to cryptocurrency markets for millions of potential users.",
                "cover_img": "https://example.com/exchange.jpg",
                "id": 100003,
                "news_url": "https://example.com/exchange-news",
                "origin_url": "https://example.com/exchange-news",
                "published_at": int(time.time()),
                "sort_id": 1,
                "source_id": "exchange_news_789",
                "source_name": "Exchange Updates",
                "source_type": 5,
                "type": 2
            }
        ]
    
    def connect_to_server(self, url):
        """Connect to the news WebSocket server"""
        print(f"Simulating connection to WebSocket server: {url}")
        self.ws_url = url
        self.reconnect_attempts = 0
        
        # Simulate connection delay
        QTimer.singleShot(500, self._on_connected)
    
    def reconnect(self):
        """Attempt to reconnect to the WebSocket server"""
        if self.is_connected or self.reconnect_attempts >= self.max_reconnect_attempts:
            self.reconnect_timer.stop()
            return
            
        print(f"Simulating reconnection to WebSocket (Attempt {self.reconnect_attempts + 1})")
        self.reconnect_attempts += 1
        self.connect_to_server(self.ws_url)
    
    def disconnect_from_server(self):
        """Disconnect from the news WebSocket server"""
        print("Disconnecting from simulated WebSocket")
        self.is_connected = False
        self.news_timer.stop()
        self.reconnect_timer.stop()
        self.disconnected.emit()
    
    def _on_connected(self):
        """Handle successful WebSocket connection"""
        print("Mock WebSocket connected")
        self.is_connected = True
        self.reconnect_attempts = 0
        self.reconnect_timer.stop()
        self.connected.emit()
        
        # Start timer to simulate receiving news quickly for the first time
        # then use longer intervals for subsequent news
        self.news_timer.start(3000)  # Show first news in 3 seconds
    
    def _simulate_news_message(self):
        """Simulate receiving a news message"""
        if not self.is_connected:
            return
            
        # Select a random sample news item
        news_data = random.choice(self.sample_news).copy()
        # Update the timestamp to current time
        news_data["published_at"] = int(time.time())
        
        print(f"Simulating received news: {news_data['title']}")
        
        # Create and emit news model
        try:
            news_model = self._create_news_model(news_data)
            if news_model:
                self.news_received.emit(news_model)
        except Exception as e:
            print(f"Error creating news model: {e}")
        
        # Set next interval for news simulation
        new_interval = random.randint(10000, 30000)  # Random interval between 10-30 seconds
        self.news_timer.setInterval(new_interval)
    
    def _is_valid_news_data(self, data):
        """Validate if the received data has the required fields for a news item"""
        required_fields = ['title', 'abstract']
        return all(field in data for field in required_fields)
    
    def _create_news_model(self, data):
        """Create a NewsModel instance from the received data"""
        try:
            # Get values with fallbacks for missing fields
            news = NewsModel(
                abstract=data.get('abstract', ''),
                cover_img=data.get('cover_img', ''),
                id=data.get('id'),
                news_url=data.get('news_url', ''),
                origin_url=data.get('origin_url', ''),
                published_at=int(data.get('published_at', 0)),
                sort_id=int(data.get('sort_id', 1)),
                source_id=data.get('source_id', ''),
                source_name=data.get('source_name', 'Unknown'),
                source_type=int(data.get('source_type', 0)),
                title=data.get('title', 'No Title'),
                type=data.get('type')
            )
            return news
        except (ValueError, TypeError) as e:
            print(f"Error creating NewsModel from data: {e}")
            return None 