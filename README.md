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
- live2d-py
- Other dependencies listed in pyproject.toml

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aicompanionx/XBuddy-Desktop-PyQt5.git
   cd XBuddy-Desktop-PyQt5
   ```

2. Install uv
   ```bash
   # on macos or linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # on windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   # then install uv tox tool
   uv tool install tox --with tox-uv
   ```

3. Install dependencies:
   ```bash
   cd XBuddy-Desktop-PyQt5
   uv sync
   ```

4. Run the application:
   ```bash
   python ./xbuddy/main.py
   ```

5. For development
   ```bash
   npm install
   npx husky init
   echo "npx --no -- commitlint --edit $1" > ./.husky/commit-msg
   echo "pre-commit run --hook-stage pre-commit" > ./.husky/pre-commit
   ```


## Configuration

The application uses the `xbuddy/settings.py` file for settings.

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
