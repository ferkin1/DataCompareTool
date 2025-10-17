from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QWidget, QVBoxLayout, QFrame,
                               QLabel, QFileDialog, QTableView, QStackedLayout, QHBoxLayout, QPlainTextEdit,
                               QSizePolicy, QHeaderView, QAbstractItemView, QMenu)
from PySide6.QtCore import Qt, Signal, QItemSelection, QItemSelectionModel
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
        preview_df = df.head(20).copy()
        self._model.set_df(preview_df if preview_df is not None else pd.DataFrame())

        # Table
        self._table.setMinimumHeight(160)
        self._table.setMinimumWidth(100)
        self._table.setSortingEnabled(False)
        self._table.setAcceptDrops(False)
        self._table.resizeColumnsToContents()
        self._table.resizeRowsToContents()
        self._table.setFrameShape(QFrame.NoFrame)
        self._table.setShowGrid(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectColumns)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # Headers
        vert_header = self._table.verticalHeader()
        vert_header.setVisible(True)
        vert_header.setFixedWidth(25)

        h_header = self._table.horizontalHeader()
        h_header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        h_header.setStretchLastSection(False)
        h_header.setDefaultSectionSize(50)
        h_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self._table.resizeColumnsToContents()

        MAX_WIDTH = 60
        for col in range(self._model.columnCount()):
            width = min(self._table.columnWidth(col), MAX_WIDTH)
            self._table.setColumnWidth(col, width)
            h_header.setSectionResizeMode(col, QHeaderView.Fixed)

        h_header.setSectionsClickable(True)
        h_header.setSectionResizeMode(QHeaderView.Interactive)
        h_header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        h_header.customContextMenuRequested.connect(self._on_header_menu)
        h_header.sectionClicked.connect(self._on_header_click)


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

    def _on_header_click(self, table_index: int):
        rows = self._model.rowCount()
        if rows == 0:
            return
        top_left = self._model.index(0, table_index)
        bottom_right = self._model.index(rows - 1, table_index)
        selection = QItemSelection(top_left, bottom_right)

        selection_model = self._table.selectionModel()
        mods = QApplication.keyboardModifiers()
        if not (mods & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier)):
            selection_model.clearSelection()

        selection_model.select(selection, QItemSelectionModel.SelectionFlag.Select |
                               QItemSelectionModel.SelectionFlag.Columns)
        self._table.setCurrentIndex(top_left)

    def _on_header_menu(self, pos):
        header = self._table.horizontalHeader()
        l_index = header.logicalIndexAt(pos)
        if l_index < 0:
            return
        menu = QMenu(self)
        action_select = menu.addAction("Select Column")
        action_sort_asc = menu.addAction("Sort Ascending")
        action_sort_desc = menu.addAction("Sort Descending")

        action = menu.exec(header.mapToGlobal(pos))
        if action is action_select:
            self._on_header_click(l_index)
        elif action is action_sort_asc:
            self._model.sort(l_index, Qt.SortOrder.AscendingOrder)
            header.setSortIndicator(l_index, Qt.SortOrder.AscendingOrder)
            header.setSortIndicatorShown(True)
        elif action is action_sort_desc:
            self._model.sort(l_index, Qt.SortOrder.DescendingOrder)
            header.setSortIndicator(l_index, Qt.SortOrder.DescendingOrder)
            header.setSortIndicatorShown(True)
