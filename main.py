from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                              QTextEdit, QListWidget, QWidget, QLineEdit,QLabel,QDialog,QComboBox,QDialogButtonBox,QMessageBox)
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import Qt, QTimer, QAbstractTableModel
from parcer import csv_to_list

from ui.ui_main import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #Подгрузка словаря
        try:
            self.word_dictionary = csv_to_list('dictionary.csv')
            if not self.word_dictionary:
                self.word_dictionary = ["Словарь пуст"]
        except Exception as e:
            print(f"Ошибка загрузки словаря: {e}")
            self.word_dictionary = ["Ошибка загрузки словаря"]

        #Подтверждение выбора исходной и целевой СК
        self.ui.listWidget.itemClicked.connect(lambda item: self.apply_suggestion(item,self.ui.lineEdit,self.ui.listWidget))
        self.ui.listWidget_2.itemClicked.connect(lambda item: self.apply_suggestion(item,self.ui.lineEdit_2,self.ui.listWidget_2))

        #Работа с QLineEdit при определении исходной и целевой СК
        self.ui.lineEdit.textChanged.connect(lambda : self.on_text_changed(self.ui.lineEdit,self.ui.listWidget))
        self.ui.lineEdit_2.textChanged.connect(lambda : self.on_text_changed(self.ui.lineEdit_2,self.ui.listWidget_2))

        #При инициации приложения отображение перечня
        self.update_suggestions("",self.ui.listWidget)
        self.update_suggestions("",self.ui.listWidget_2)

        #Работа с подгрузкой и выгрузкой данных
        self.model = PandasModel()
        self.ui.tableView.setModel(self.model)
    
    def on_text_changed(self,lineedit:QLineEdit,listwidget:QListWidget):
        text = lineedit.text().strip()
        QTimer.singleShot(300, lambda: self.check_and_update_suggestions(text,listwidget))

    def check_and_update_suggestions(self, current_text:str,listwidget:QListWidget):
        """Обновляет подсказки и скрывает список если текст совпадает с подсказкой"""
        # Сначала проверяем совпадение с текущим текстом
        if self.check_exact_match(current_text,listwidget):
            listwidget.hide()
            return
            
        # Если точного совпадения нет - обновляем подсказки
        self.update_suggestions(current_text,listwidget)

    def check_exact_match(self, text:str,listwidget:QListWidget):
        """Проверяет точное совпадение текста с любой подсказкой"""
        if not text:
            return False
            
        for i in range(listwidget.count()):
            if listwidget.item(i).text().lower() == text.lower():
                return True
        return False

    def update_suggestions(self, current_text:str,listwidget:QListWidget):
        """Обновление списка подсказок"""
        listwidget.clear()
        
        if not current_text:
            suggestions = self.word_dictionary
        else:
            suggestions = [
                word for word in self.word_dictionary 
                if str(current_text).lower() in str(word).lower()
            ]
        
        if suggestions:
            for word in suggestions:
                listwidget.addItem(str(word))
            listwidget.show()
        else:
            listwidget.hide()

    def apply_suggestion(self,item, lineedit:QLineEdit,listwidget:QListWidget):
        """Применяет выбранную подсказку"""     
        lineedit.setText(item.text())
        listwidget.hide()
        lineedit.setFocus()
    
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
        
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()