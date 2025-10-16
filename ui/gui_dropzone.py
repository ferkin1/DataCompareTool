from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QWidget, QVBoxLayout, QFrame,
                               QLabel, QFileDialog, QTableView, QStackedLayout, QHBoxLayout, QPlainTextEdit,
                               QSizePolicy)
from PySide6.QtCore import Qt, Signal
from back_end import build_ext_filter
from ui.gui_dataframemodel import DataFrameModel
import pandas as pd
import os


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

        self._model = DataFrameModel()
        self._table = QTableView()
        self._table.setModel(self._model)

        self.stack = QStackedLayout(self)

        # Stack 0: Drop UI
        drop_stack = QWidget()
        vert_0 = QVBoxLayout(drop_stack)
        vert_0.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title = QLabel(title)
        self.title.setStyleSheet("font-size: 14px; color: #f9f9f9;")

        self.plus = QPushButton("+")
        self.plus.setStyleSheet("font-size: 48px; color: #f9f9f9;")
        self.plus.setCursor(Qt.PointingHandCursor)
        self.plus.clicked.connect(self.click_plus)
        self.plus.setAcceptDrops(False)
        vert_0.addWidget(self.title)
        vert_0.addWidget(self.plus)


        # Stack 1: Preview UI
        preview_stack = QWidget()
        vert_1 = QVBoxLayout(preview_stack)

        topbar = QHBoxLayout()
        self.status = QPlainTextEdit()
        self.status.setReadOnly(True)
        self.status.setStyleSheet("color:#bbb; font-size:12px")
        self.status.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.status.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.status.setMinimumWidth(80)
        self.status.setMaximumWidth(200)
        self.status.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.status.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # status_height = self.status.fontMetrics().height()
        self.status.setFixedHeight(40)

        self.replace_button = QPushButton("Replace Dataset")
        self.replace_button.setCursor(Qt.PointingHandCursor)
        self.replace_button.setFixedHeight(20)
        self.replace_button.clicked.connect(self.click_plus)

        topbar.addWidget(self.status)
        topbar.addStretch(1)
        topbar.addWidget(self.replace_button)

        vert_1.addLayout(topbar)
        vert_1.addWidget(self._table)

        self.stack.addWidget(drop_stack)
        self.stack.addWidget(preview_stack)
        self.stack.setCurrentIndex(0)

    def dragEnterEvent(self, event):
        md = event.mimeData()
        # if event.mimeData().hasUrls():
        if md.hasUrls() and any(url.isLocalFile() for url in md.urls()):
            self.setProperty("dragOver", True)
            self.style().unpolish(self); self.style().polish(self)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        # urls = event.mimeData().urls()
        urls = [url for url in event.mimeData().urls() if url.isLocalFile()]
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

        filename, _ = QFileDialog.getOpenFileName(self, caption="Select a Data File", filter=filetypes)
        if filename:
            self.fileSelected.emit(filename)

    def set_preview(self, df: pd.DataFrame, source_path: str | None = None):
        self._model.set_df(df if df is not None else pd.DataFrame())

        self._table.setMinimumHeight(160)
        self._table.setMaximumWidth(400)
        self._table.setSortingEnabled(True)
        self._table.setAcceptDrops(False)
        self._table.resizeColumnsToContents()
        self._table.resizeRowsToContents()
        self._table.verticalHeader().setVisible(False)
        self._table.setFrameShape(QFrame.NoFrame)
        self._table.setShowGrid(True)
        self._table.horizontalHeader().setStretchLastSection(False)

        header = self._table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        if source_path:
            name = os.path.basename(source_path)
            self.set_status_text(f"{name} :: {len(df)} rows :: {len(df.columns)} columns")
        self.stack.setCurrentIndex(1)

    def clear_preview(self):
        self._model.set_df(pd.DataFrame())
        self.status.setText("")
        self.stack.setCurrentIndex(0)

    def set_status_text(self, text: str, tooltip: bool = True):
        self.status.setPlainText(text)
        if tooltip:
            self.status.setToolTip(text)

        self.status.horizontalScrollBar().setValue(0)

