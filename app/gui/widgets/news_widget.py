from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea, QFrame, QHBoxLayout
from PyQt5.QtGui import QFont, QFontMetrics, QPixmap
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import datetime
from app.model.news_model import NewsModel

class NewsDetailWindow(QWidget):
    """Window to display the full news title and content"""
    def __init__(self, news: NewsModel):
        super().__init__()
        self.setWindowTitle("XBuddy/News")
        self.setMinimumWidth(400) # Set a minimum width, height will be adaptive
        self.setMaximumWidth(600)
        self.setMinimumHeight(200)
        self.setMaximumHeight(800)
        self.news = news
        
        # Network manager for loading images
        self.network_manager = QNetworkAccessManager(self) # Added network manager
        
        # Set background color to white
        self.setStyleSheet("QWidget { background-color: white; }")
        # QWidget needs autoFillBackground to be true for QPalette to work reliably for background
        # Using stylesheet is often more direct for simple background color.

        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Create title label
        self.title_label = QLabel(self.news.title)
        self.title_label.setFont(QFont("Arial", 18))
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setText(f'''<h4 style="line-height: 1.3; margin: 0; color: #000000; font-weight: normal; text-wrap: wrap;">
            {self.news.title}
        </h4>''')

        # Create content label
        self.content_label = QLabel(self.news.abstract)
        self.content_label.setFont(QFont("Arial", 14))
        self.content_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.content_label.setWordWrap(True)
        self.content_label.setTextFormat(Qt.RichText)
        self.content_label.setText(f'''<p style="line-height: 1.3; margin: 0; text-align: justify; color: #000000;">
            {self.news.abstract}
        </p>''')

        # Create source label (no alignment needed here, layout handles it)
        self.source_label = QLabel(self.news.source_name)
        self.source_label.setFont(QFont("Arial", 12))
        self.source_label.setStyleSheet("""
            QLabel {
                color: #000000;
                background-color: #D0D8FF; /* Light blue background */
                border-radius: 10px; /* Slightly smaller radius */
                padding: 5px 10px; /* Adjust padding */
                margin-right: 5px; /* Add some margin if needed */
            }
        """)
        # No need for setTextFormat or setText again unless using HTML inside

        # Create and format published at label
        try:
            published_date = datetime.datetime.fromtimestamp(self.news.published_at)
            formatted_date = published_date.strftime("%B %d, %Y %H:%M")
        except (TypeError, ValueError):
            formatted_date = "Invalid Date"
            
        self.published_at_label = QLabel(f"Published: {formatted_date}")
        self.published_at_label.setFont(QFont("Arial", 12))
        self.published_at_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.published_at_label.setStyleSheet("color: #555555;") # Slightly muted color
        # No need for setTextFormat or setText again

        #Create source and published at layout (QHBoxLayout)
        source_published_at_layout = QHBoxLayout()
        source_published_at_layout.addWidget(self.source_label, 0) # Add source label with stretch factor 0 (takes minimum space)
        source_published_at_layout.addStretch(1) # Add stretch to push published_at to the right
        source_published_at_layout.addWidget(self.published_at_label, 0) # Add published_at label with stretch factor 0

        # Create a cover image label
        self.cover_image_label = QLabel("Loading image...")
        self.cover_image_label.setAlignment(Qt.AlignCenter)
        # Set a fixed height for the image area
        self.fixed_image_height = 100 # Define desired fixed height
        self.cover_image_label.setFixedHeight(self.fixed_image_height)
        # Width will be determined by image aspect ratio
        # Remove setMaximumWidth if previously set
        self.cover_image_label.setStyleSheet(""" 
            QLabel {
                background-color: #f0f0f0; /* Placeholder background */
                border-radius: 10px;
                color: #888888;
                padding: 10px;
                /* Width will adjust, no need to set it here */
            }
        """)
        # Load image if URL exists
        cover_img_url = getattr(self.news, 'cover_img', None)
        if cover_img_url and isinstance(cover_img_url, str) and cover_img_url.strip():
            self.load_image(cover_img_url)
        else:
            self.cover_image_label.setText("No image available")

        # Create origin link label
        self.origin_link_label = QLabel() # Create empty label first
        self.origin_link_label.setFont(QFont("Arial", 12))
        self.origin_link_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter) # Center the link text
        self.origin_link_label.setStyleSheet("margin-top: 10px;") # Add space above
        self.origin_link_label.setTextFormat(Qt.RichText) # Set format to handle HTML
        self.origin_link_label.setOpenExternalLinks(True) # Enable opening links
        # Set the actual HTML link content
        origin_url = getattr(self.news, 'origin_url', '#') # Safely get URL
        self.origin_link_label.setText(f'''
            <a href="{origin_url}" style="color: #0066cc; text-decoration: none;">
                Origin News Link
            </a>
        ''')
        # No need for setCursor or setToolTip, setOpenExternalLinks handles interaction
        
        # Add widgets and the horizontal layout to the main vertical layout
        layout.addWidget(self.title_label)
        layout.addLayout(source_published_at_layout)
        layout.addWidget(self.cover_image_label)
        layout.addWidget(self.content_label)
        layout.addStretch(1) # Add stretch HERE to push link to bottom
        layout.addWidget(self.origin_link_label) # Add the link label HERE

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)  # Remove the frame
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hide vertical scrollbar
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 

        scroll_widget = QWidget()
        scroll_widget.setLayout(layout)
        scroll_area.setWidget(scroll_widget)

        main_layout = QVBoxLayout(self) # Set main layout directly on self
        main_layout.setContentsMargins(0,0,0,0) # No margins for the main layout holding the scroll area
        main_layout.addWidget(scroll_area)
        
        self.adjustSize() # Adjust window size to fit content

    # --- Image Loading Methods --- 
    def load_image(self, image_url):
        """Load image from URL asynchronously."""
        try:
            request = QNetworkRequest(QUrl(image_url))
            reply = self.network_manager.get(request)
            reply.finished.connect(lambda rep=reply: self.on_image_loaded(rep))
        except Exception as e:
            print(f"Error creating network request for {image_url}: {e}")
            self.cover_image_label.setText("Invalid image URL")

    def on_image_loaded(self, reply: QNetworkReply):
        """Handle the loaded image data when the network request finishes."""
        if reply.error() == QNetworkReply.NoError:
            img_data = reply.readAll()
            pixmap = QPixmap()
            if pixmap.loadFromData(img_data):
                # --- Scaling based on Fixed Height --- 
                scaled_pixmap = pixmap.scaledToHeight(self.fixed_image_height, Qt.SmoothTransformation)
                # ------------------------------------
                                    
                self.cover_image_label.setPixmap(scaled_pixmap)
                # No need to setMinimumHeight, as height is fixed
                # Optionally set fixed width to match scaled pixmap if desired, 
                # otherwise label width will adjust or depend on layout.
                # self.cover_image_label.setFixedWidth(scaled_pixmap.width())
                self.cover_image_label.setStyleSheet("border-radius: 10px;") # Reset stylesheet
            else:
                self.cover_image_label.setText("Invalid image data")
                self.cover_image_label.setStyleSheet(""" /* Keep placeholder style on error */
                    QLabel {
                        background-color: #f0f0f0; 
                        border-radius: 10px;
                        color: #888888; 
                        padding: 10px;
                    }
                """)
        else:
            error_string = reply.errorString()
            print(f"Network error loading image: {error_string}")
            self.cover_image_label.setText(f"Failed to load image")
            self.cover_image_label.setStyleSheet(""" /* Keep placeholder style on error */
                QLabel {
                    background-color: #f0f0f0; 
                    border-radius: 10px;
                    color: #888888; 
                    padding: 10px;
                }
            """)
        
        reply.deleteLater() # Ensure the reply object is cleaned up

class NewsWidget(QWidget):
    # Signal emitted when a detail window is opened
    detail_window_opened = pyqtSignal(object)
    
    def __init__(self, news: NewsModel):
        super().__init__()
        self.news = news
        self.max_lines = 2  # Reduced from 3 to fit better in fixed container
        self.detail_window = None # To hold a reference to the detail window
        self.init_ui()

    def init_ui(self):
        # Set up the main layout for the NewsWidget
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 5, 10, 5)  # Reduced vertical padding

        # Create the inner QLabel for the news content (white bubble)
        self.news_title_label = QLabel()
        self.news_title_label.setWordWrap(True) # Enable word wrapping
        self.news_title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter) # Align text
        
        # Style for the inner news content label (white bubble)
        self.news_title_label.setStyleSheet('''
            QLabel {
                background-color: white;
                color: black;
                border-radius: 10px;      
                padding: 8px;            
                font-size: 11px;          
                font-weight: normal;
            }
        ''')
        
        # Set the truncated text
        self.truncate_text()
        self.news_title_label.setFont(QFont("Arial"))
        
        main_layout.addWidget(self.news_title_label)
        self.setLayout(main_layout)

        # Style for the NewsWidget itself (outer light blue/purple bubble)
        self.setStyleSheet('''
            NewsWidget {
                background-color: #D0D8FF; /* Light blue/purple background */
                border-radius: 12px;       
                cursor: pointer;           /* Show pointer cursor on hover */
                font-weight: normal;
                margin: 3px 5px;           
                max-height: 80px;          /* Limit height to fit in container */
            }
        ''')
        
        # Set a fixed height to fit in the container
        self.setMaximumHeight(80)
        
        # Adjust size to fit content
        self.adjustSize()
        
        # Make the widget clickable
        self.setCursor(Qt.PointingHandCursor)

    def truncate_text(self):
        """Truncates text to max_lines and adds ellipsis if needed."""
        metrics = QFontMetrics(self.news_title_label.font())
        text_width = self.news_title_label.width() - 30  # Account for padding
        
        if not text_width > 0:
            # Set a default width for initial rendering
            text_width = 180

        lines = []
        current_line = ""
        words = self.news.title.split()
        line_count = 0
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            width = metrics.horizontalAdvance(test_line)
            
            if width <= text_width:
                current_line = test_line
            else:
                lines.append(current_line)
                line_count += 1
                
                # If we've reached max lines, we need to stop
                if line_count >= self.max_lines:
                    break
                    
                current_line = word
        
        # Add the last line being processed if we haven't reached max lines
        if current_line and line_count < self.max_lines:
            lines.append(current_line)
            line_count += 1
        
        # If we have more words to process but have already reached max lines,
        # or if we've filled max_lines but have more text, add ellipsis to the last line
        if line_count == self.max_lines and len(" ".join(lines).split()) < len(words):
            last_line = lines[-1]
            # Trim the last line to fit "..." at the end
            trimmed_line = last_line
            while metrics.horizontalAdvance(trimmed_line + "...") > text_width and trimmed_line:
                trimmed_line = trimmed_line[:-1]
            
            lines[-1] = trimmed_line + "..."
            
        display_text = "\n".join(lines)
        html_text = f"""
          <p style="
              line-height: 1.2;
              text-align: justify;
              font-weight: normal;
          ">
              {display_text}
          </p>
        """
        self.news_title_label.setText(html_text)
    
    def resizeEvent(self, event):
        """Handle resize events to recalculate text truncation."""
        super().resizeEvent(event)
        self.truncate_text()
    
    def mousePressEvent(self, event):
        """Handle mouse click events to show the detail window."""
        if event.button() == Qt.LeftButton:
            self.show_detail_window()
        super().mousePressEvent(event)
    
    def show_detail_window(self):
        """Shows a new window with the full news text."""
        # Check if a window is already open before creating a new one
        if self.detail_window is None or not self.detail_window.isVisible():
            self.detail_window = NewsDetailWindow(news=self.news) 
            self.detail_window.show()
            # Emit signal with the new window
            self.detail_window_opened.emit(self.detail_window)
        else:
            # If window exists, bring it to front
            self.detail_window.activateWindow()
            self.detail_window.raise_()