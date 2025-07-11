import requests
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QTimer


class ApiClient(QObject):
    """API client for external services"""

    # Signals
    request_finished = pyqtSignal(str, object)
    request_error = pyqtSignal(str, str)

    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        self.base_url = ""
        self.timeout = 10
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": f"XBuddy-Desktop/{self.app_manager.app_version}"
        }

        self.load_config()

        # Connect to event system
        self.app_manager.event_system.interaction.connect(self.on_interaction)

        # Health check timer
        self.health_check_timer = QTimer(self)
        self.health_check_timer.timeout.connect(self.check_health)
        self.health_check_timer.setInterval(60000)  # 1 minute

        if self.app_manager.config_manager.get("api.enabled", False):
            self.health_check_timer.start()

    def load_config(self):
        config = self.app_manager.config_manager
        self.base_url = config.get("api.base_url", "")
        self.timeout = config.get("api.timeout", 10)

        api_key = config.get("api.key", "")
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    @pyqtSlot(str, object)
    def on_interaction(self, interaction_type, data):
        if interaction_type == "tap" and self.app_manager.config_manager.get("api.send_interactions", False):
            self.post_async("interactions", {
                "type": interaction_type,
                "data": data
            })

    def get(self, endpoint, params=None):
        if not self.base_url:
            return None

        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API GET error: {e}")
            self.request_error.emit(endpoint, str(e))
            return None

    def post(self, endpoint, data):
        if not self.base_url:
            return None

        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.post(
                url,
                json=data,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API POST error: {e}")
            self.request_error.emit(endpoint, str(e))
            return None

    def get_async(self, endpoint, params=None):
        thread = ApiRequestThread(self, "GET", endpoint, params=params)
        thread.request_finished.connect(self._on_request_finished)
        thread.request_error.connect(self._on_request_error)
        thread.start()

    def post_async(self, endpoint, data):
        thread = ApiRequestThread(self, "POST", endpoint, data=data)
        thread.request_finished.connect(self._on_request_finished)
        thread.request_error.connect(self._on_request_error)
        thread.start()

    @pyqtSlot(str, object)
    def _on_request_finished(self, endpoint, data):
        self.request_finished.emit(endpoint, data)
        self.app_manager.event_system.api_response.emit(endpoint, data)

    @pyqtSlot(str, str)
    def _on_request_error(self, endpoint, error):
        self.request_error.emit(endpoint, error)

    def check_health(self):
        self.get_async("health")


class ApiRequestThread(QThread):
    """Thread for asynchronous API requests"""

    request_finished = pyqtSignal(str, object)
    request_error = pyqtSignal(str, str)

    def __init__(self, api_client, method, endpoint, params=None, data=None):
        super().__init__()
        self.api_client = api_client
        self.method = method
        self.endpoint = endpoint
        self.params = params
        self.data = data

    def run(self):
        if not self.api_client.base_url:
            self.request_error.emit(self.endpoint, "API base URL not configured")
            return

        url = f"{self.api_client.base_url}/{self.endpoint}"
        try:
            if self.method == "GET":
                response = requests.get(
                    url,
                    params=self.params,
                    headers=self.api_client.headers,
                    timeout=self.api_client.timeout
                )
            elif self.method == "POST":
                response = requests.post(
                    url,
                    json=self.data,
                    headers=self.api_client.headers,
                    timeout=self.api_client.timeout
                )
            else:
                self.request_error.emit(self.endpoint, f"Unsupported method: {self.method}")
                return

            response.raise_for_status()
            self.request_finished.emit(self.endpoint, response.json())
        except requests.exceptions.RequestException as e:
            self.request_error.emit(self.endpoint, str(e))
