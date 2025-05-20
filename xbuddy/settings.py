from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.absolute()
RESOURCES_DIRECTORY = PROJECT_DIR / "resources"

DEFAULT_MODEL_SCALE = 0.6
QSS = (RESOURCES_DIRECTORY / "style.css").read_text(encoding="utf-8")
FPS = 60

API_SERVER = "localhost:8080"
