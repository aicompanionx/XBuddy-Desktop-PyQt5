import json
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class PhishingChecker(QObject):
    """API interface for checking if a URL is a phishing website"""
    
    # Signals
    check_finished = pyqtSignal(str, bool, str)
    check_error = pyqtSignal(str, str)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        
        # Connect API client signals
        self.api_client.request_finished.connect(self._on_request_finished)
        self.api_client.request_error.connect(self._on_request_error)
    
    def check_url(self, url, lang="en"):
        """
        Check if a URL is a phishing website
        
        Args:
            url (str): URL to check
            lang (str): Language for response messages, default is English
        """
        data = {
            "url": url,
            "lang": lang
        }
        
        # Send asynchronous request
        self.api_client.post_async("check-phishing", data)
    
    @pyqtSlot(str, object)
    def _on_request_finished(self, endpoint, response):
        """Handle API request completion callback"""
        if endpoint != "check-phishing":
            return
            
        try:
            if response.get("code") == 0 and "data" in response:
                data = response["data"]
                self.check_finished.emit(
                    data.get("url", ""),
                    data.get("isPhishing", False),
                    data.get("message", "")
                )
            else:
                self.check_error.emit("", response.get("msg", "Unknown error"))
        except Exception as e:
            self.check_error.emit("", f"Failed to parse response: {str(e)}")
    
    @pyqtSlot(str, str)
    def _on_request_error(self, endpoint, error):
        """Handle API request error callback"""
        if endpoint == "check-phishing":
            self.check_error.emit("", f"Request failed: {error}")
