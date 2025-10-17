from PySide6.QtWidgets import (QApplication,
                               QMainWindow,
                               QPushButton,
                               QWidget,
                               QVBoxLayout,
                               QHBoxLayout,
                               QTableView,
                               QSplitter,
                               QMessageBox,
                               QFormLayout)
from PySide6.QtCore import Qt
from .gui_dropzone import DropZoneUI
from .gui_dataframemodel import DataFrameModel
from back_end.data_service import DataService
import pandas as pd

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.datasrvc = DataService()
        self.setWindowTitle("DataComp")

        self.df_a: pd.DataFrame() | None = None
        self.df_b: pd.DataFrame() | None = None

        self.file_btn = QPushButton("File")
        self.options_btn = QPushButton("Options")

        self.layout = QFormLayout()

        # Top Bar
        top_layout = QHBoxLayout()

        top_layout.addWidget(self.file_btn)


        # Center Preview
        center_widget = QWidget()
        self.setCentralWidget(center_widget)
        vbox = QVBoxLayout(center_widget)

        self.table = QTableView()
        self.model = DataFrameModel()
        self.table.setModel(self.model)

        # Data Panels
        self.dropA = DropZoneUI("Select/Drop File A")
        self.dropB = DropZoneUI("Select/Drop File B")

        # Split Data Panels
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.dropA)
        self.splitter.addWidget(self.table)
        self.splitter.addWidget(self.dropB)
        self.splitter.setStretchFactor(0,1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setStretchFactor(2, 1)
        self.splitter.setChildrenCollapsible(False)

        vbox.addWidget(self.splitter)

        self.dropA.fileSelected.connect(lambda path: self.load_panel("a", path))
        self.dropB.fileSelected.connect(lambda path: self.load_panel("b", path))

        self.dropA.setMaximumWidth(500)
        self.dropB.setMaximumWidth(500)

        self.layout.addRow(top_layout)
        self.layout.addRow(vbox)


    def load_panel(self, side: str, path: str):
        try:
            df = self.datasrvc.get_data(path)
        except Exception as e:
            QMessageBox.critical(self, "Failed to load Data", str(e))
            return

        preview = df.copy()

        if side.lower() == "a":
            self.df_a = df
            self.dropA.set_preview(preview, path)

        else:
            self.df_b = df
            self.dropB.set_preview(preview, path)



if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec()