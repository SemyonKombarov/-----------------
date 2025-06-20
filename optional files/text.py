from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                              QTextEdit, QListWidget, QWidget)
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import Qt, QTimer
from parcer import csv_to_list


class TextEditWithSuggestions(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Текстовый редактор с подсказками")
        self.setGeometry(100, 100, 500, 400)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Текстовое поле
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Введите текст здесь...")
        self.text_edit.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.text_edit)
        
        # Список подсказок
        self.suggestions_list = QListWidget()
        self.suggestions_list.setMaximumHeight(150)
        self.suggestions_list.itemClicked.connect(self.apply_suggestion)
        layout.addWidget(self.suggestions_list)
        
        # Загрузка словаря
        try:
            self.word_dictionary = csv_to_list('dictionary.csv')
            if not self.word_dictionary:
                self.word_dictionary = ["Словарь пуст"]
        except Exception as e:
            print(f"Ошибка загрузки словаря: {e}")
            self.word_dictionary = ["Ошибка загрузки словаря"]
        
        # Показываем полный словарь при старте
        self.update_suggestions("")

    def on_text_changed(self):
        text = self.text_edit.toPlainText().strip()
        QTimer.singleShot(300, lambda: self.check_and_update_suggestions(text))

    def check_and_update_suggestions(self, current_text):
        """Обновляет подсказки и скрывает список если текст совпадает с подсказкой"""
        # Сначала проверяем совпадение с текущим текстом
        if self.check_exact_match(current_text):
            self.suggestions_list.hide()
            return
            
        # Если точного совпадения нет - обновляем подсказки
        self.update_suggestions(current_text)

    def check_exact_match(self, text):
        """Проверяет точное совпадение текста с любой подсказкой"""
        if not text:
            return False
            
        for i in range(self.suggestions_list.count()):
            if self.suggestions_list.item(i).text().lower() == text.lower():
                return True
        return False

    def update_suggestions(self, current_text):
        """Обновляет список подсказок"""
        self.suggestions_list.clear()
        
        if not current_text:
            suggestions = self.word_dictionary
        else:
            suggestions = [
                word for word in self.word_dictionary 
                if str(current_text).lower() in str(word).lower()
            ]
        
        if suggestions:
            for word in suggestions:
                self.suggestions_list.addItem(str(word))
            self.suggestions_list.show()
        else:
            self.suggestions_list.hide()

    def apply_suggestion(self, item):
        """Применяет выбранную подсказку"""
        if item is None:
            return
            
        self.text_edit.setPlainText(item.text())
        self.suggestions_list.hide()
        self.text_edit.setFocus()


if __name__ == "__main__":
    app = QApplication([])
    window = TextEditWithSuggestions()
    window.show()
    app.exec()