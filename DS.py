import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableView, 
                              QVBoxLayout, QWidget, QMessageBox, QPushButton,
                              QHBoxLayout, QDialog, QComboBox, QLabel, QDialogButtonBox)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QClipboard

class ColumnMappingDialog(QDialog):
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Сопоставление столбцов")
        
        layout = QVBoxLayout(self)
        
        self.combo_boxes = {}
        
        # Добавляем выбор для каждого специального столбца
        layout.addWidget(QLabel("Выберите столбцы для специальных полей:"))
        
        # Наименование
        layout.addWidget(QLabel("Наименование:"))
        cb_name = QComboBox()
        cb_name.addItem("Не использовать", -1)
        for i, col in enumerate(columns):
            cb_name.addItem(f"Столбец {i+1} ({col})", i)
        self.combo_boxes['name'] = cb_name
        layout.addWidget(cb_name)
        
        # Долгота/X
        layout.addWidget(QLabel("Долгота/X:"))
        cb_lon = QComboBox()
        cb_lon.addItem("Не использовать", -1)
        for i, col in enumerate(columns):
            cb_lon.addItem(f"Столбец {i+1} ({col})", i)
        self.combo_boxes['lon'] = cb_lon
        layout.addWidget(cb_lon)
        
        # Широта/Y
        layout.addWidget(QLabel("Широта/Y:"))
        cb_lat = QComboBox()
        cb_lat.addItem("Не использовать", -1)
        for i, col in enumerate(columns):
            cb_lat.addItem(f"Столбец {i+1} ({col})", i)
        self.combo_boxes['lat'] = cb_lat
        layout.addWidget(cb_lat)
        
        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_mapping(self):
        return {
            'name': self.combo_boxes['name'].currentData(),
            'lon': self.combo_boxes['lon'].currentData(),
            'lat': self.combo_boxes['lat'].currentData()
        }

class PandasModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        self._headers = []
        self.column_mapping = {'name': -1, 'lon': -1, 'lat': -1}

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._data[0]) if self._data else 0

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and self._data:
            return str(self._data[index.row()][index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section] if section < len(self._headers) else None
        return None

    def setData(self, data, headers=None):
        self.beginResetModel()
        self._data = data
        self._headers = headers if headers is not None else [f"Столбец {i+1}" for i in range(len(data[0]))] if data else []
        self.endResetModel()
        
    def set_column_mapping(self, mapping):
        self.column_mapping = mapping
        
    def swap_lat_lon_headers(self):
        lat_col = self.column_mapping['lat']
        lon_col = self.column_mapping['lon']
        
        if lat_col == -1 or lon_col == -1:
            return False
            
        self.beginResetModel()
        # Меняем только заголовки, не трогая данные
        self._headers[lat_col], self._headers[lon_col] = self._headers[lon_col], self._headers[lat_col]
        # Обновляем mapping
        self.column_mapping['lat'], self.column_mapping['lon'] = self.column_mapping['lon'], self.column_mapping['lat']
        self.endResetModel()
        
        return True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Table Paste Example with Column Mapping")
        self.setGeometry(100, 100, 800, 600)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Button layout
        button_layout = QHBoxLayout()
        
        # Swap Headers Button
        self.swap_button = QPushButton("Поменять названия Широта/Y и Долгота/X")
        self.swap_button.clicked.connect(self.swap_lat_lon_headers)
        button_layout.addWidget(self.swap_button)
        
        main_layout.addLayout(button_layout)

        # Table View
        self.tableView = QTableView()
        self.model = PandasModel()
        self.tableView.setModel(self.model)
        main_layout.addWidget(self.tableView)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            self.paste_from_clipboard()
        elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            self.copy_to_clipboard()
        else:
            super().keyPressEvent(event)

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        
        if not text:
            return
            
        try:
            # Parse clipboard text (assuming tab-separated values)
            rows = text.split('\n')
            data = []
            for row in rows:
                if row.strip():
                    data.append(row.split('\t'))
            
            if not data:
                return
                
            # Показываем диалог для сопоставления столбцов
            dialog = ColumnMappingDialog(data[0] if data else [], self)
            if dialog.exec() == QDialog.Accepted:
                mapping = dialog.get_mapping()
                self.model.set_column_mapping(mapping)
                
                # Устанавливаем данные в модель
                headers = [f"Столбец {i+1}" for i in range(len(data[0]))]
                
                # Обновляем заголовки для специальных столбцов
                if mapping['name'] != -1:
                    headers[mapping['name']] = "Наименование"
                if mapping['lon'] != -1:
                    headers[mapping['lon']] = "Долгота/X"
                if mapping['lat'] != -1:
                    headers[mapping['lat']] = "Широта/Y"
                
                self.model.setData(data, headers)
                
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось вставить данные: {str(e)}")
    
    def copy_to_clipboard(self):
        if not self.model._data:
            return
            
        clipboard = QApplication.clipboard()
        text = ""
        
        # Добавляем заголовки
        text += "\t".join(str(header) for header in self.model._headers) + "\n"
        
        # Добавляем данные
        for row in self.model._data:
            text += "\t".join(str(cell) for cell in row) + "\n"
        
        clipboard.setText(text.strip())
        QMessageBox.information(self, "Успех", "Таблица скопирована в буфер обмена")
    
    def swap_lat_lon_headers(self):
        if not self.model.swap_lat_lon_headers():
            QMessageBox.warning(self, "Ошибка", 
                               "Не удалось поменять названия столбцов.\n"
                               "Убедитесь, что столбцы 'Широта/Y' и 'Долгота/X' были правильно определены при вставке.")
        else:
            QMessageBox.information(self, "Успех", 
                                  "Названия столбцов 'Широта/Y' и 'Долгота/X' успешно поменялись местами")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())