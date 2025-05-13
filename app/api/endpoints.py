"""API endpoints definitions"""


class Endpoints:
    """API endpoint constants"""

    # Health check endpoint
    HEALTH = "health"

    # User endpoints
    USER_LOGIN = "user/login"
    USER_LOGOUT = "user/logout"
    USER_PROFILE = "user/profile"

    # Model endpoints
    MODELS_LIST = "models/list"
    MODELS_DOWNLOAD = "models/download"
    MODELS_INFO = "models/info"

    # Interaction endpoints
    INTERACTIONS_LOG = "interactions/log"
    INTERACTIONS_STATS = "interactions/stats"

    # Chat endpoints
    CHAT_SEND = "chat/send"
    CHAT_HISTORY = "chat/history"
    CHAT_WS = "chat/ws"  # WebSocket endpoint for real-time chat

    # System endpoints
    SYSTEM_UPDATE = "system/update"
    SYSTEM_CONFIG = "system/config"
    
    # News endpoints
    NEWS_WS = "news/ws"  # WebSocket endpoint for real-time news


class ApiRoutes:
    """Helper class for working with API routes"""

    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def get_url(self, endpoint):
        """Get full URL for an endpoint"""
        return f"{self.base_url}/{endpoint}"

    def get_ws_url(self, endpoint):
        """Get WebSocket URL for an endpoint"""
        # Convert http(s):// to ws(s)://
        ws_base = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        return f"{ws_base}/{endpoint}"

    def health(self):
        """Health check endpoint"""
        return self.get_url(Endpoints.HEALTH)

    def login(self):
        """Login endpoint"""
        return self.get_url(Endpoints.USER_LOGIN)

    def logout(self):
        """Logout endpoint"""
        return self.get_url(Endpoints.USER_LOGOUT)

    def profile(self):
        """User profile endpoint"""
        return self.get_url(Endpoints.USER_PROFILE)

    def models_list(self):
        """Models list endpoint"""
        return self.get_url(Endpoints.MODELS_LIST)

    def model_download(self, model_id):
        """Model download endpoint"""
        return f"{self.get_url(Endpoints.MODELS_DOWNLOAD)}/{model_id}"

    def model_info(self, model_id):
        """Model info endpoint"""
        return f"{self.get_url(Endpoints.MODELS_INFO)}/{model_id}"

    def log_interaction(self):
        """Log interaction endpoint"""
        return self.get_url(Endpoints.INTERACTIONS_LOG)

    def interaction_stats(self):
        """Interaction stats endpoint"""
        return self.get_url(Endpoints.INTERACTIONS_STATS)

    def chat_send(self):
        """Chat send endpoint"""
        return self.get_url(Endpoints.CHAT_SEND)

    def chat_history(self):
        """Chat history endpoint"""
        return self.get_url(Endpoints.CHAT_HISTORY)

    def system_update(self):
        """System update endpoint"""
        return self.get_url(Endpoints.SYSTEM_UPDATE)

    def system_config(self):
        """System config endpoint"""
        return self.get_url(Endpoints.SYSTEM_CONFIG)

    def news_ws(self):
        """News WebSocket endpoint"""
        return self.get_ws_url(Endpoints.NEWS_WS)

    def chat_ws(self):
        """Chat WebSocket endpoint"""
        return self.get_ws_url(Endpoints.CHAT_WS)
