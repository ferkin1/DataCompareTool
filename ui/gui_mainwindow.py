from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout
from .gui_dropzone import DropZoneUI

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("DataComp")

        main_container = QWidget()
        self.setCentralWidget(main_container)

        layout = QHBoxLayout(main_container)

        self.dropA = DropZoneUI("Select/Drop File A")
        self.dropB = DropZoneUI("Select/Drop File B")

        layout.addWidget(self.dropA)
        layout.addWidget(self.dropB)





if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec()