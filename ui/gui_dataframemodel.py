from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
import pandas as pd


class DataFrameModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame | None = None, parent=None):
        super().__init__()
        self._df = data

    def set_df(self, data: pd.DataFrame):
        self.beginResetModel()
        self._df = data if data is not None else pd.DataFrame()
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return 0 if self._df is None else len(self._df)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return 0 if self._df is None else len(self._df.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or self._df is None:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            val = self._df.iat[index.row(), index.column()]
            if pd.isna(val):
                return ""
            return str(val)

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole or self._df is None:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return str(self._df.columns[section])
        try:
            return str(self._df.index[section])
        except Exception:
            return str(section)

    def sort(self, column, order):
        if self._df is None or self._df.empty:
            return
        col_name = self._df.columns[column]
        ascending = order == Qt.SortOrder.AscendingOrder
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(by=col_name,
                             ascending=ascending,
                             inplace=True,
                             ignore_index=True)
        self.layoutChanged.emit()