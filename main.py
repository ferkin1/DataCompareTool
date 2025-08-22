from PySide6.QtWidgets import QApplication
from ui.gui_mainwindow import MainWindow
import sys


def main():
    app = QApplication(sys.argv)
    winui = MainWindow()
    winui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()