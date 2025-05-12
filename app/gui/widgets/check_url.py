from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMessageBox

from app.api.check_api import PhishingChecker


class CheckURL(QObject):
    """
    Class for checking URLs for phishing attempts and displaying results to the user.
    """
    
    # Signal emitted when check is complete
    check_completed = pyqtSignal(str, bool, str)
    
    def __init__(self, api_client, parent=None):
        """
        Initialize the URL checker.
        
        Args:
            api_client: API client for making requests
            parent: Parent QObject
        """
        super().__init__(parent)
        
        # Create the phishing checker
        self.checker = PhishingChecker(api_client)
        
        # Connect signals
        self.checker.check_finished.connect(self._on_check_finished)
        self.checker.check_error.connect(self._on_check_error)
    
    def check_url(self, url):
        """
        Check if a URL is a phishing website.
        
        Args:
            url (str): URL to check
        """
        # Validate URL
        if not url:
            self._show_error("Error", "Please enter a valid URL")
            return
            
        # Clean URL if needed
        url = url.strip()
        
        # Send URL for checking
        try:
            self.checker.check_url(url, "en")
        except Exception as e:
            self._show_error("Error", f"Failed to check URL: {str(e)}")
    
    @pyqtSlot(str, bool, str)
    def _on_check_finished(self, url, is_phishing, message):
        """
        Handle check completion.
        
        Args:
            url (str): Checked URL
            is_phishing (bool): Whether URL is a phishing site
            message (str): Additional message from the API
        """
        # Emit signal for other components
        self.check_completed.emit(url, is_phishing, message)
        
        # Show appropriate message box
        if is_phishing:
            self._show_warning("Security Warning", 
                              f"The URL {url} appears to be a phishing website.\n\n{message}")
        else:
            self._show_info("Security Check", 
                           f"The URL {url} appears to be safe.\n\n{message}")
    
    @pyqtSlot(str, str)
    def _on_check_error(self, url, error):
        """
        Handle check error.
        
        Args:
            url (str): URL that was being checked
            error (str): Error message
        """
        self._show_error("Check Failed", 
                        f"Could not complete security check for {url or 'the URL'}.\n\n{error}")
    
    def _show_warning(self, title, message):
        """Show warning message box."""
        QMessageBox.warning(None, title, message)
    
    def _show_info(self, title, message):
        """Show information message box."""
        QMessageBox.information(None, title, message)
    
    def _show_error(self, title, message):
        """Show error message box."""
        QMessageBox.critical(None, title, message)
