from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtGui import QPixmap, QMouseEvent, QWheelEvent, QImage
from PyQt6.QtCore import Qt, QPoint
import sys
import os

class TransparentWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Окно без рамок и всегда сверху
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")  # Полностью прозрачный фон окна

        # Загружаем изображение
        self.image_label = QLabel(self)
        self.image = QPixmap()  # Изначально пустое изображение
        self.opacity = 150  # Прозрачность (0 - полностью прозрачное, 255 - непрозрачное)
        self.update_image_opacity()

        self.image_label.setScaledContents(True)

        # Начальный размер окна (по размеру изображения)
        self.resize(300, 300)  # Размер по умолчанию, если изображение не загружено

        # Создаем метку для зоны перетаскивания
        self.drag_zone = QLabel(self)
        self.drag_zone.setText("Перетащите изображение сюда")
        self.drag_zone.setStyleSheet("background-color: rgba(0, 0, 0, 50); color: white; border: 2px dashed gray; padding: 20px;")
        self.drag_zone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_zone.resize(self.size())
        
        # Флаги для обработки событий
        self.dragging = False
        self.resizing = False
        self.changing_opacity = False  # Флаг для изменения прозрачности
        self.drag_start = QPoint()
        self.scale_factor = 1.0  # Коэффициент масштабирования

        # Устанавливаем для окна перетаскивание
        self.setAcceptDrops(True)

    def update_image_opacity(self):
        """Создаёт полупрозрачное изображение, сохраняя черный цвет"""
        if self.image.isNull():
            return  # Если изображение не загружено, ничего не делаем

        image = self.image.toImage().convertToFormat(QImage.Format.Format_ARGB32)
        for y in range(image.height()):
            for x in range(image.width()):
                pixel = image.pixelColor(x, y)
                if pixel.alpha() > 0:  # Изменяем только непрозрачные пиксели
                    pixel.setAlpha(self.opacity)
                    image.setPixelColor(x, y, pixel)
        self.image_label.setPixmap(QPixmap.fromImage(image))

    def keyPressEvent(self, event):
        """Обрабатывает нажатие клавиш, например, Ctrl+Q для выхода"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Q:
            self.close_application()  # Закрытие приложения при Ctrl+Q

    def mousePressEvent(self, event: QMouseEvent):
        """Определяет действие: перемещение, изменение размера или настройка прозрачности"""
        if event.button() == Qt.MouseButton.LeftButton:
            if event.pos().x() > self.width() - 20 and event.pos().y() > self.height() - 20:
                self.resizing = True  # Режим изменения размера
            else:
                self.dragging = True  # Режим перемещения
            self.drag_start = event.globalPosition().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            self.changing_opacity = True  # Включаем изменение прозрачности

    def mouseMoveEvent(self, event: QMouseEvent):
        """Перемещение окна или изменение его размера"""
        if self.dragging:
            delta = event.globalPosition().toPoint() - self.drag_start
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.drag_start = event.globalPosition().toPoint()
        elif self.resizing:
            delta = event.globalPosition().toPoint() - self.drag_start
            new_width = max(50, self.width() + delta.x())
            new_height = max(50, self.height() + delta.y())
            self.resize(new_width, new_height)
            self.image_label.resize(new_width, new_height)  # Изменяем размер изображения
            self.drag_start = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Сбрасывает флаги после отпускания кнопки мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
        elif event.button() == Qt.MouseButton.RightButton:
            self.changing_opacity = False  # Останавливаем изменение прозрачности

    def wheelEvent(self, event: QWheelEvent):
        """Масштабирование при зажатой ЛКМ, изменение прозрачности при зажатой ПКМ"""
        if self.dragging:  # Если зажата ЛКМ — изменяем масштаб
            delta = event.angleDelta().y() / 120
            self.scale_factor += delta * 0.1
            self.scale_factor = max(0.2, min(3.0, self.scale_factor))

            # Вычисляем новый размер
            new_width = int(self.image.width() * self.scale_factor)
            new_height = int(self.image.height() * self.scale_factor)
            self.resize(new_width, new_height)
            self.image_label.resize(new_width, new_height)

        elif self.changing_opacity:  # Если зажата ПКМ — изменяем прозрачность
            delta = event.angleDelta().y() / 120
            self.opacity += int(delta * 15)
            self.opacity = max(10, min(255, self.opacity))  # Ограничиваем от 10 до 255
            self.update_image_opacity()  # Применяем новую прозрачность

    def dragEnterEvent(self, event):
        """Обрабатывает событие перетаскивания файлов в окно"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Обрабатывает событие отпускания файла в окно"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()  # Путь к файлу
            if os.path.isfile(file_path) and file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                self.load_image(file_path)  # Загружаем изображение

    def load_image(self, file_path):
        """Загружает изображение в окно"""
        self.image = QPixmap(file_path)
        self.update_image_opacity()
        self.resize(self.image.width(), self.image.height())
        self.image_label.resize(self.size())  # Изменяем размер изображения
        self.drag_zone.hide()  # Скрываем зону перетаскивания


app = QApplication(sys.argv)
window = TransparentWindow()
window.show()
sys.exit(app.exec())
