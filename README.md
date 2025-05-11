# XBuddy Desktop

A Live2D desktop pet application built with PyQt5 and OpenGL.

## Features

- Live2D model rendering using OpenGL
- Transparent window with frameless design
- System tray integration
- Configurable behavior and appearance
- API integration for additional functionality

## Requirements

- Python 3.11+
- PyQt5
- PyOpenGL
- Other dependencies listed in requirements.txt

## Installation

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

## Configuration

The application uses a `config.json` file for settings. If no configuration file exists, a default one will be created automatically.

Key configuration options:
- `model`: The default Live2D model to load
- `window`: Window position, size, and transparency settings
- `behavior`: Pet behavior settings
- `api`: API endpoint configurations

## Project Structure

```
xbuddy_desktop/
├── main.py                    # Application entry point
├── requirements.txt           # Project dependencies
├── config.json                # Configuration file
├── app/                       # Application core code
│   ├── core/                  # Core functionality
│   ├── gui/                   # GUI related code
│   ├── live2d/                # Live2D related code
│   └── api/                   # API related code
├── resources/                 # Resource files
│   ├── models/                # Live2D model files
│   ├── sounds/                # Audio resources
│   └── icons/                 # Icon resources
└── tests/                     # Test code
```

## Adding Live2D Models

Place your Live2D models in the `resources/models` directory. Each model should be in its own subdirectory containing the model files.

Example structure:
```
resources/models/
├── model1/
│   ├── model.json (or model3.json)
│   ├── texture_00.png
│   └── ... (other model files)
└── model2/
    ├── model.json (or model3.json)
    ├── texture_00.png
    └── ... (other model files)
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 