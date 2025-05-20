from xbuddy.gui.pet_widgets import PetWidget
from xbuddy.gui.utils import run
from xbuddy.gui.widgets.tray_icon import TrayIcon


class MainWindow(PetWidget):
    def __init__(self):
        super().__init__()
        self.tray_icon = TrayIcon()
        self.tray_icon.show()


if __name__ == "__main__":
    run(MainWindow)
