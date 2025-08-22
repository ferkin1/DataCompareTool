from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QWidget, QVBoxLayout, QFrame,
                               QLabel, QFileDialog)
from PySide6.QtCore import Qt, Signal
from back_end import build_ext_filter

class DropZoneUI(QFrame):
    fileSelected = Signal(str)
    ext_map = {
        "CSV / Text Files": ['.csv', '.txt', '.tsv'],
        "Excel Files": ['.xlsx', '.xls', '.xlsm', '.xlsb', '.ods'],
        "JSON Files": ['.json'],
        "HTML Files": ['.html'],
        "Parquet Files": ['.parquet'],
        "Pickle Files": ['.pkl'],
        "Stata Files": ['.dta'],
        "SAS Files": ['.sas7bdat', '.xpt'],
        "Feather Files": ['.feather']
    }

    def __init__(self, title="Drop file here", parent=None):
        super().__init__(parent)

        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #999;
                border-radius: 10px;
                background-color: #181818;
                }
            QFrame[dragOver="true"] { 
                border-color: #1f6fe5; 
                background: #203040; }
                """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.plus = QPushButton("+")
        self.plus.setStyleSheet("font-size: 48px; color: #f9f9f9;")
        self.plus.clicked.connect(self.click_plus)
        self.plus.setAcceptDrops(False)

        self.title = QLabel(title)
        self.title.setStyleSheet("font-size: 14px; color: #f9f9f9;")

        layout.addWidget(self.title)
        layout.addWidget(self.plus)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("dragOver", True)
            self.style().unpolish(self); self.style().polish(self)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path:
                self.fileSelected.emit(path)
                self.setProperty("dragOver", False)
                self.style().unpolish(self); self.style().polish(self)
                event.accept()
                # print(path)

    def dragLeaveEvent(self, event):
        self.setProperty("dragOver", False)
        self.style().unpolish(self); self.style().polish(self)
        event.accept()


    def click_plus(self):
        filetypes = build_ext_filter(self.ext_map)

        file_dialog = QFileDialog.getOpenFileName(self, caption="Select a Data File", filter=filetypes)
        if file_dialog:
            self.fileSelected.emit(file_dialog)

