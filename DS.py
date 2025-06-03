import sys
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, 
    QLineEdit, QMessageBox, QHeaderView
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt
from pyproj import Transformer, CRS

class CoordinateConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Конвертер координат")
        self.setGeometry(100, 100, 1000, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Секция ввода точек
        points_layout = QHBoxLayout()
        main_layout.addLayout(points_layout)
        
        # Таблица для ввода точек
        self.points_table = QTableWidget()
        self.points_table.setColumnCount(3)
        self.points_table.setHorizontalHeaderLabels(["№", "X", "Y"])
        self.points_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.add_point_row()
        points_layout.addWidget(self.points_table)
        
        # Кнопки управления точками
        points_btn_layout = QVBoxLayout()
        points_layout.addLayout(points_btn_layout)
        
        self.add_point_btn = QPushButton("Добавить точку")
        self.add_point_btn.clicked.connect(self.add_point_row)
        points_btn_layout.addWidget(self.add_point_btn)
        
        self.remove_point_btn = QPushButton("Удалить точку")
        self.remove_point_btn.clicked.connect(self.remove_point_row)
        points_btn_layout.addWidget(self.remove_point_btn)
        
        # Секция систем координат
        crs_layout = QHBoxLayout()
        main_layout.addLayout(crs_layout)
        
        crs_layout.addWidget(QLabel("Исходная СК (EPSG):"))
        self.source_crs_input = QLineEdit("4326")
        crs_layout.addWidget(self.source_crs_input)
        
        crs_layout.addWidget(QLabel("Целевая СК (EPSG):"))
        self.target_crs_input = QLineEdit("3857")
        crs_layout.addWidget(self.target_crs_input)
        
        # Кнопка конвертации
        self.convert_btn = QPushButton("Конвертировать координаты")
        self.convert_btn.clicked.connect(self.convert_coordinates)
        main_layout.addWidget(self.convert_btn)
        
        # Веб-виджет для отображения точек
        self.web_view = QWebEngineView()
        main_layout.addWidget(self.web_view, 1)
        
        # Инициализация карты
        self.init_map()

    def add_point_row(self):
        row_count = self.points_table.rowCount()
        self.points_table.insertRow(row_count)
        
        # Номер точки
        point_num = QTableWidgetItem(str(row_count + 1))
        point_num.setFlags(point_num.flags() ^ Qt.ItemIsEditable)
        self.points_table.setItem(row_count, 0, point_num)
        
        # Координата X
        self.points_table.setItem(row_count, 1, QTableWidgetItem("0.0"))
        
        # Координата Y
        self.points_table.setItem(row_count, 2, QTableWidgetItem("0.0"))

    def remove_point_row(self):
        if self.points_table.rowCount() > 1:
            self.points_table.removeRow(self.points_table.rowCount() - 1)
            # Обновляем номера точек
            for row in range(self.points_table.rowCount()):
                self.points_table.item(row, 0).setText(str(row + 1))

    def init_map(self):
        """Инициализирует пустую карту"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Карта точек</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <style>
                #map { height: 100%; }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                var map = L.map('map').setView([0, 0], 2);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }).addTo(map);
            </script>
        </body>
        </html>
        """
        self.web_view.setHtml(html)

    def show_points_on_map(self, points):
        """Отображает точки на карте с помощью JavaScript"""
        # Преобразуем точки в формат JSON для передачи в JavaScript
        points_js = json.dumps(points)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Карта точек</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <style>
                #map {{ height: 100%; }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                // Инициализация карты
                var map = L.map('map').setView([0, 0], 2);
                
                // Добавление слоя OpenStreetMap
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }}).addTo(map);
                
                // Точки для отображения
                var points = {points_js};
                
                // Добавление маркеров на карту
                var bounds = new L.LatLngBounds();
                for (var i = 0; i < points.length; i++) {{
                    var point = points[i];
                    var marker = L.marker([point.y, point.x]).addTo(map);
                    marker.bindPopup("<b>Точка №" + point.num + "</b><br>X: " + point.x + "<br>Y: " + point.y);
                    bounds.extend(marker.getLatLng());
                }}
                
                // Автоматическое масштабирование карты
                if (points.length > 0) {{
                    map.fitBounds(bounds);
                }}
            </script>
        </body>
        </html>
        """
        self.web_view.setHtml(html)

    def convert_coordinates(self):
        """Конвертирует координаты и отображает результат на карте"""
        try:
            # Получение EPSG кодов
            source_epsg = self.source_crs_input.text().strip()
            target_epsg = self.target_crs_input.text().strip()
            
            # Валидация EPSG
            if not source_epsg or not target_epsg:
                raise ValueError("EPSG коды не могут быть пустыми")
                
            CRS.from_epsg(int(source_epsg))
            CRS.from_epsg(int(target_epsg))
            
            # Сбор исходных точек
            points = []
            for row in range(self.points_table.rowCount()):
                try:
                    num = int(self.points_table.item(row, 0).text())
                    x = float(self.points_table.item(row, 1).text())
                    y = float(self.points_table.item(row, 2).text())
                    points.append({"num": num, "x": x, "y": y})
                except:
                    raise ValueError(f"Некорректные данные в строке {row + 1}")
            
            if not points:
                raise ValueError("Должна быть указана хотя бы одна точка")
            
            # Создание трансформера
            transformer = Transformer.from_crs(
                f"EPSG:{source_epsg}", 
                f"EPSG:{target_epsg}", 
                always_xy=True
            )
            
            # Конвертация координат
            converted_points = []
            for point in points:
                x, y = point["x"], point["y"]
                new_x, new_y = transformer.transform(x, y)
                converted_points.append({
                    "num": point["num"],
                    "x": round(new_x, 6),
                    "y": round(new_y, 6)
                })
            
            # Отображение результатов на карте
            self.show_points_on_map(converted_points)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CoordinateConverterApp()
    window.show()
    sys.exit(app.exec())