<p align="center">
    <img src="./docs/logo.png" alt="XBuddy Logo" />
</p>

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-Latest-41CD52?logo=qt&logoColor=white)
![OpenGL](https://img.shields.io/badge/OpenGL-Latest-5586A4?logo=opengl&logoColor=white)
![JSON](https://img.shields.io/badge/JSON-Config-000000?logo=json&logoColor=white)
![Live2D](https://img.shields.io/badge/Live2D-Integration-FF69B4)

# 📖 About the Project <a name="about-the-project"></a>

**XBuddy Desktop** is a desktop pet application, and this repository contains its frontend implementation (based on PyQt5 and OpenGL). The application provides user interfaces for news feeds, phishing link detection, Twitter/token analysis, AI chat, chat content recognition, and emotion reminders.

## 🔑 Key Features <a name="key-features"></a>

- 📰 News Feed - Automatically fetches the latest information
- 🎣 Phishing Link Detection - Protects users' online security
- 🤖 AI Chat - Intelligent conversation and sentiment analysis
- 📊 Data Analysis - Twitter/token trend tracking

## 💻 Getting Started <a name="getting-started"></a>

### Requirements <a name="requirements"></a>

- Python 3.11+
- PyQt5
- PyOpenGL
- Other dependencies listed in requirements.txt

### Setup <a name="setup"></a>

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/xbuddy_desktop.git
   cd xbuddy_desktop
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

### Configuration <a name="configuration"></a>

The application uses a `config.json` file for settings. If no configuration file exists, a default one will be created automatically.

Key configuration options:
- `model`: The default Live2D model to load
- `window`: Window position, size, and transparency settings
- `behavior`: Pet behavior settings
- `api`: API endpoint configurations

## 📂 Project Structure <a name="project-structure"></a>

```
XBuddy-Desktop-PyQt5/
├── app/                    # Main application code
│   ├── api/                # API clients and interfaces
│   │   ├── check_api.py    # API checking functionality
│   │   └── client.py       # API client implementation
│   ├── core/               # Core functionality modules
│   │   ├── app_manager.py  # Application manager
│   │   ├── config_manager.py # Configuration management
│   │   └── event_system.py # Event system
│   ├── gui/                # Graphical user interface
│   │   ├── live2d/         # Live2D model rendering
│   │   ├── widgets/        # Custom UI components
│   │   ├── main_window.py  # Main window implementation
│   │   └── tray_icon.py    # System tray icon
│   └── services/           # Application services
│       └── browser_monitor_service.py # Browser monitoring service
├── docs/                   # Documentation and resources
│   └── logo.png            # Project logo
├── resources/              # Resource files
│   └── icons/              # Icon resources
├── tests/                  # Test code
├── config.json             # Application configuration file
├── main.py                 # Application entry point
├── requirements.txt        # Project dependencies
└── LICENSE                 # License file
```

## 📄 License <a name="license"></a>

This project is licensed under the [CC BY-NC](./LICENSE) License (Creative Commons Attribution-NonCommercial).
