
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                              QListWidget, QLineEdit,QFileDialog,
                              QLabel, QDialog, QComboBox, QDialogButtonBox, 
                              QMessageBox, QHeaderView, QTableView)
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt, QTimer, QAbstractTableModel, QModelIndex

from pyproj import Transformer
from dictionary import data
from ui.ui_main import Ui_mainWindow

class MainWindow(QMainWindow):
    """Класс инициализирующий главное окно со всем содержимым"""
    def __init__(self):
        """Инициализация, подвязки с основным функционалом"""
        super(MainWindow,self).__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)

        #Подгрузка словаря
        self.word_dictionary = data

        #Подтверждение выбора исходной и целевой СК
        self.ui.listWidget.itemClicked.connect(lambda item: 
                self.apply_suggestion(item,self.ui.lineEdit,self.ui.listWidget))
        self.ui.listWidget_2.itemClicked.connect(lambda item: 
                self.apply_suggestion(item,self.ui.lineEdit_2,self.ui.listWidget_2))

        #Работа с QLineEdit при определении исходной и целевой СК
        self.ui.lineEdit.textChanged.connect(lambda : 
                self.on_text_changed(self.ui.lineEdit,self.ui.listWidget))
        self.ui.lineEdit_2.textChanged.connect(lambda : 
                self.on_text_changed(self.ui.lineEdit_2,self.ui.listWidget_2))

        #При инициации приложения отображение перечня
        self.update_suggestions("",self.ui.listWidget)
        self.update_suggestions("",self.ui.listWidget_2)

        #Работа с подгрузкой и выгрузкой данных
        self.model = PandasModel()
        self.ui.tableView.setModel(self.model)

        #Включаем редактирование для обеих таблиц
        self.ui.tableView.setEditTriggers(QTableView.DoubleClicked | QTableView.EditKeyPressed)
        self.ui.tableView_2.setEditTriggers(QTableView.DoubleClicked | QTableView.EditKeyPressed)
        
        #Настраиваем поведение при редактировании
        self.ui.tableView.setSelectionBehavior(QTableView.SelectItems)
        self.ui.tableView.setSelectionMode(QTableView.ContiguousSelection)
        self.ui.tableView_2.setSelectionBehavior(QTableView.SelectItems)
        self.ui.tableView_2.setSelectionMode(QTableView.ContiguousSelection)

        #Кнопка для реверса
        self.ui.pushButton_3.clicked.connect(self.swap_lat_lon_headers)

        #Пересчёт координат
        self.ui.pushButton_4.clicked.connect(self.perform_translation)

        #Настройка копирования по Ctrl+C
        self.ui.tableView.setSelectionBehavior(QTableView.SelectItems)
        self.ui.tableView.setSelectionMode(QTableView.ContiguousSelection)
        self.ui.tableView_2.setSelectionBehavior(QTableView.SelectItems)
        self.ui.tableView_2.setSelectionMode(QTableView.ContiguousSelection)
        
        #Подключаем обработчики Ctrl+C
        QShortcut(QKeySequence.Copy, self.ui.tableView, context=Qt.WidgetShortcut, 
                 activated=lambda: self.copy_selection(self.ui.tableView))
        QShortcut(QKeySequence.Copy, self.ui.tableView_2, context=Qt.WidgetShortcut,
                 activated=lambda: self.copy_selection(self.ui.tableView_2))
        
        #Выгрузка в эксель
        self.ui.pushButton_5.clicked.connect(self.export_xlsx)

        #Добавить новую точку
        self.ui.pushButton.clicked.connect(self.add_coords_manualy)

        #Кнопка помощь
        self.ui.pushButton_2.clicked.connect(self.help)

    def help(self):
        QMessageBox.information(self, "А помоши не будет...", "По всем остальным вопросам обращаться по адресу: Kombarov.SVya@contractor.gazprom-neft.ru")
        
    def add_coords_manualy(self):
        """Добавляет новую строку в таблицу координат"""
        model = self.ui.tableView.model()
        
        if not model or model.rowCount() == 0:
            # Если таблица пуста, добавляем строку с заголовками
            data = [["", "", ""]]  # Пустые значения для трех столбцов
            headers = ["Наименование", "Долгота/X", "Широта/Y"]
            model.setTableData(data, headers)  # Изменено на setTableData
            
            # Устанавливаем mapping для столбцов
            model.set_column_mapping({
                'name': 0,
                'lon': 1,
                'lat': 2
            })
        else:
            # Если таблица не пуста, добавляем новую строку
            row_position = model.rowCount()
            model.beginInsertRows(QModelIndex(), row_position, row_position)
            model._data.append(["" for _ in range(model.columnCount())])
            model.endInsertRows()
        
        # Прокручиваем к новой строке
        self.ui.tableView.scrollToBottom()
        header = self.ui.tableView.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Растягиваем все столбцы равномерно
        header.setDefaultAlignment(Qt.AlignLeft)  # Выравнивание заголовков по левому краю

    def export_xlsx(self):
        """Экспорт данных из tableview_2 в файл CSV (UTF-8)"""
        # Получаем модель из tableview_2
        model = self.ui.tableView_2.model()
        
        if not model or model.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта")
            return
        
        # Получаем данные из модели
        data = []
        headers = []
        
        # Получаем заголовки
        for col in range(model.columnCount()):
            headers.append(model.headerData(col, Qt.Horizontal, Qt.DisplayRole))
        
        # Получаем данные
        for row in range(model.rowCount()):
            row_data = []
            for col in range(model.columnCount()):
                index = model.index(row, col)
                row_data.append(model.data(index, Qt.DisplayRole))
            data.append(row_data)
        
        # Создаем DataFrame
        df = pd.DataFrame(data, columns=headers)
        
        # Открываем диалог сохранения файла с фильтром для CSV
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл CSV",
            "",
            "CSV Files (*.csv);;All Files (*)",
            options=QFileDialog.Option(0)  # Или просто удалите параметр options
        )
        
        if not file_path:
            return  # Пользователь отменил сохранение
        
        # Добавляем расширение .csv, если его нет
        if not file_path.lower().endswith('.csv'):
            file_path += '.csv'
        
        try:
            # Сохраняем в CSV с кодировкой UTF-8
            df.to_csv(file_path, index=False, encoding='utf-8-sig')  # utf-8-sig для BOM (лучшая совместимость с Excel)
            QMessageBox.information(self, "Успех", f"Файл успешно сохранен:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
            return
    
    def copy_selection(self, table_view:QTableView):
        """Копирует выделенный диапазон ячеек в буфер обмена"""
        selection = table_view.selectionModel()
        if not selection.hasSelection():
            return
            
        selected = selection.selectedIndexes()
        if not selected:
            return
            
        # Определяем границы выделения
        min_row = min(index.row() for index in selected)
        max_row = max(index.row() for index in selected)
        min_col = min(index.column() for index in selected)
        max_col = max(index.column() for index in selected)
        
        # Получаем модель
        model = table_view.model()
        clipboard_data = []
        
        # Формируем данные для копирования
        for row in range(min_row, max_row + 1):
            row_data = []
            for col in range(min_col, max_col + 1):
                index = model.index(row, col)
                row_data.append(str(model.data(index)))
            clipboard_data.append("\t".join(row_data))
        
        # Копируем в буфер обмена
        QApplication.clipboard().setText("\n".join(clipboard_data))
        
        # Уведомление пользователя
        QMessageBox.information(self, "Копирование", 
                              f"Скопировано {len(selected)} ячеек", 
                              QMessageBox.Ok)  

    def perform_translation(self):
        """Выполняет перевод координат и отображает результаты в tableview_2"""
        source_crs = self.ui.lineEdit.text().split()
        target_crs = self.ui.lineEdit_2.text().split()
        
        if not source_crs or not target_crs:
            QMessageBox.warning(self, "Ошибка", "Не указана исходная или целевая СК")
            return
            
        try:
            # Создаем экземпляр Perevod
            translator = Perevod(source_crs, target_crs, self.model)
            
            # Получаем результаты перевода
            translated_coords = translator.from_source_to_target_crs()
            
            # Создаем модель для отображения результатов
            result_model = PandasModel()
            
            # Подготавливаем данные для отображения
            result_data = []
            
            # Определяем индексы нужных столбцов
            lon_col = self.model.column_mapping['lon']
            lat_col = self.model.column_mapping['lat']
            name_col = self.model.column_mapping['name']
            
            if lon_col == -1 or lat_col == -1:
                QMessageBox.warning(self, "Ошибка", "Не удалось определить столбцы с координатами")
                return
                
            # Формируем заголовки
            headers = []
            if name_col != -1:
                headers.append("Наименование")
            headers.extend(["Долгота/X", "Широта/Y"])
            
            # Заполняем данные
            for i, (orig_row, new_coords) in enumerate(zip(self.model._data, translated_coords)):
                row_data = []
                
                # Добавляем наименование, если есть
                if name_col != -1:
                    row_data.append(orig_row[name_col])
                    
                # Добавляем только пересчитанные координаты
                row_data.extend([
                    str(new_coords[0]),
                    str(new_coords[1])
                ])
                
                result_data.append(row_data)
            
            # Устанавливаем данные в модель
            result_model.setTableData(result_data, headers)
            
            # Отображаем модель в tableview_2
            self.ui.tableView_2.setModel(result_model)
            
            # Настраиваем отображение таблицы
            header = self.ui.tableView_2.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)
            header.setDefaultAlignment(Qt.AlignLeft)
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось выполнить перевод координат: {str(e)}")

    def on_text_changed(self,lineedit:QLineEdit,listwidget:QListWidget):
        """Обновление подсказок"""
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
        elif event.key() == Qt.Key_Delete:
            self.delete_selected_rows()
        else:
            super().keyPressEvent(event)

    def delete_selected_rows(self):
        """Удаляет выбранные строки по нажатию клавиши Delete"""
        selection = self.ui.tableView.selectionModel()
        if not selection.hasSelection():
            return
            
        selected_rows = set(index.row() for index in selection.selectedRows())
        if not selected_rows:
            return
            
        # Удаляем строки в обратном порядке, чтобы индексы не сдвигались
        for row in sorted(selected_rows, reverse=True):
            self.model.removeRow(row)

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
                
                self.model.setTableData(data, headers)

                #Растягивание таблиц, чтоб красиво было
                header = self.ui.tableView.horizontalHeader()
                header.setSectionResizeMode(QHeaderView.Stretch)  # Растягиваем все столбцы равномерно
                header.setDefaultAlignment(Qt.AlignLeft)  # Выравнивание заголовков по левому краю
                
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
        if not index.isValid():
            return None
            
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return str(self._data[index.row()][index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section] if section < len(self._headers) else None
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.isValid():
            try:
                self._data[index.row()][index.column()] = value
                self.dataChanged.emit(index, index)
                return True
            except Exception as e:
                print(f"Error setting data: {e}")
                return False
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return super().flags(index) | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        """Метод для редактирования ячеек (оставляем с оригинальным именем)"""
        if role == Qt.EditRole and index.isValid():
            try:
                self._data[index.row()][index.column()] = value
                self.dataChanged.emit(index, index)
                return True
            except Exception as e:
                print(f"Error setting data: {e}")
                return False
        return False

    def setTableData(self, data, headers=None):
        """Метод для установки данных таблицы (переименован из setData)"""
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
    
    def removeRow(self, row, parent=QModelIndex()):
        """Удаляет строку из модели"""
        if 0 <= row < len(self._data):
            self.beginRemoveRows(parent, row, row)
            del self._data[row]
            self.endRemoveRows()
            return True
        return False

    def removeRows(self, rows):
        """Удаляет несколько строк из модели"""
        if not rows:
            return False
            
        # Сортируем в обратном порядке, чтобы индексы не сдвигались
        for row in sorted(rows, reverse=True):
            self.removeRow(row)
        return True

class Perevod(QAbstractTableModel):
    def __init__(self, source_crs, target_crs, model, parent = None):
        super().__init__(parent)
        numbers = "0123456789"
        self.source_crs = int("".join([i for i in source_crs[-1] if i in numbers]))
        self.target_crs = int("".join([i for i in target_crs[-1] if i in numbers]))
        self.model = model._data
        self.headers = model._headers
        self.from_source_to_target_crs()
        
        
    def from_source_to_target_crs(self):
        lst = []    
        transformer = Transformer.from_crs(self.source_crs, self.target_crs)
        
        # Находим индексы столбцов с координатами
        for x, y in enumerate(self.headers):
            if y == "Долгота/X":
                long = x
            if y == "Широта/Y":
                lat = x
        
        for i in self.model:
            try:
                # Преобразуем координаты, заменяя запятые на точки для корректного преобразования в float
                tmp = transformer.transform(
                    float(i[lat].replace(",", ".")), 
                    float(i[long].replace(",", "."))
                )
                lst.append(tmp)
            except Exception as e:
                print(f"Ошибка преобразования координат: {e}")
                lst.append(("Ошибка", "Ошибка"))
        
        return lst
        
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()