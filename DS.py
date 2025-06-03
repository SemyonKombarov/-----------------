import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableView, 
                               QVBoxLayout, QWidget, QMessageBox)
from PySide6.QtCore import Qt, QMimeData, QAbstractTableModel
import pandas as pd
import numpy as np


class PandasModel(QAbstractTableModel):
    """Модель для отображения DataFrame в TableView"""
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            else:
                return str(self._data.index[section])
        return None

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            try:
                self._data.iloc[index.row(), index.column()] = value
                self.dataChanged.emit(index, index)
                return True
            except Exception as e:
                QMessageBox.warning(None, "Ошибка", f"Не удалось изменить данные: {e}")
                return False
        return False

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable


class ExcelTableView(QTableView):
    """Кастомный TableView с поддержкой вставки из Excel"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setSelectionBehavior(QTableView.SelectItems)
        self.setSelectionMode(QTableView.ExtendedSelection)

    def keyPressEvent(self, event):
        """Обработка Ctrl+V для вставки данных из буфера обмена"""
        if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            self.paste_from_clipboard()
        else:
            super().keyPressEvent(event)

    def paste_from_clipboard(self):
        """Вставка данных из буфера обмена"""
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        if mime_data.hasText():
            text = mime_data.text()
            try:
                # Парсим текст как табличные данные (разделенные табами и переводами строк)
                rows = text.split('\n')
                data = []
                for row in rows:
                    if row.strip():
                        data.append(row.split('\t'))
                
                if data:
                    # Преобразуем в DataFrame
                    df = pd.DataFrame(data)
                    
                    # Создаем или обновляем модель
                    current_model = self.model()
                    if current_model is None:
                        model = PandasModel(df)
                        self.setModel(model)
                    else:
                        # Вставка в текущую позицию
                        current_index = self.currentIndex()
                        start_row = current_index.row() if current_index.isValid() else 0
                        start_col = current_index.column() if current_index.isValid() else 0
                        
                        # Расширяем DataFrame если нужно
                        needed_rows = start_row + len(df)
                        needed_cols = start_col + len(df.columns)
                        
                        current_rows = current_model.rowCount()
                        current_cols = current_model.columnCount()
                        
                        # Добавляем строки если нужно
                        if needed_rows > current_rows:
                            empty_rows = pd.DataFrame(
                                np.nan, 
                                index=range(current_rows, needed_rows),
                                columns=current_model._data.columns
                            )
                            current_model._data = pd.concat([current_model._data, empty_rows])
                            self.model().layoutChanged.emit()
                        
                        # Добавляем колонки если нужно
                        if needed_cols > current_cols:
                            for col in range(current_cols, needed_cols):
                                current_model._data[f'Column_{col+1}'] = np.nan
                            self.model().layoutChanged.emit()
                        
                        # Вставляем данные
                        for r in range(len(df)):
                            for c in range(len(df.columns)):
                                target_row = start_row + r
                                target_col = start_col + c
                                if target_row < current_model.rowCount() and target_col < current_model.columnCount():
                                    value = df.iloc[r, c]
                                    current_model.setData(current_model.index(target_row, target_col), value, Qt.EditRole)
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось вставить данные: {e}")

    def dragEnterEvent(self, event):
        """Обработка события перетаскивания"""
        if event.mimeData().hasFormat("application/x-qt-windows-mime;value=\"Csv\"") or \
           event.mimeData().hasFormat("text/plain"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Обработка события отпускания при перетаскивании"""
        mime_data = event.mimeData()
        
        if mime_data.hasFormat("application/x-qt-windows-mime;value=\"Csv\"") or \
           mime_data.hasFormat("text/plain"):
            text = mime_data.text()
            try:
                # Парсим текст как табличные данные
                rows = text.split('\n')
                data = []
                for row in rows:
                    if row.strip():
                        data.append(row.split('\t'))
                
                if data:
                    df = pd.DataFrame(data)
                    model = PandasModel(df)
                    self.setModel(model)
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось обработать перетаскиваемые данные: {e}")
            event.acceptProposedAction()
        else:
            event.ignore()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel to TableView")
        self.setGeometry(100, 100, 800, 600)
        
        # Создаем центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Создаем TableView
        self.tableView = ExcelTableView()
        layout.addWidget(self.tableView)
        
        # Инструкция для пользователя
        self.statusBar().showMessage("Используйте Ctrl+V для вставки из Excel или перетащите диапазон ячеек")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())