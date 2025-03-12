from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QGraphicsOpacityEffect
from PyQt6.QtGui import QPixmap, QMouseEvent, QWheelEvent
from PyQt6.QtCore import Qt, QPoint
import sys
import os

class TransparentWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Окно без рамок и всегда сверху
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Метка изображения
        self.image_label = QLabel(self)
        self.image = QPixmap()  
        self.opacity = 150  

        # Прозрачность через эффект
        self.opacity_effect = QGraphicsOpacityEffect()
        self.image_label.setGraphicsEffect(self.opacity_effect)
        self.update_image_opacity()

        self.image_label.setScaledContents(True)

        # Зона перетаскивания
        self.drag_zone = QLabel("Перетащите изображение сюда", self)
        self.drag_zone.setStyleSheet("background-color: rgba(0, 0, 0, 50); color: white; border: 2px dashed gray; padding: 20px;")
        self.drag_zone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_zone.resize(300, 300)

        # Флаги для обработки событий
        self.setAcceptDrops(True)
        self.dragging = False
        self.changing_opacity = False
        self.scale_factor = 1.0
        self.drag_start = QPoint()

    def update_image_opacity(self):
        """Обновляет прозрачность изображения"""
        self.opacity_effect.setOpacity(self.opacity / 255.0)

    def keyPressEvent(self, event):
        """Закрытие программы при нажатии Ctrl+Q"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Q:
            os._exit(0)  # Принудительно завершаем процесс

    def mousePressEvent(self, event: QMouseEvent):
        """Обрабатывает нажатие мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start = event.globalPosition().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            self.changing_opacity = True  

    def mouseMoveEvent(self, event: QMouseEvent):
        """Перемещение окна"""
        if self.dragging:
            delta = event.globalPosition().toPoint() - self.drag_start
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.drag_start = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Остановка действий"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
        elif event.button() == Qt.MouseButton.RightButton:
            self.changing_opacity = False  

    def wheelEvent(self, event: QWheelEvent):
        """Масштабирование (при зажатой ЛКМ) или изменение прозрачности (при зажатой ПКМ)"""
        delta = event.angleDelta().y() / 120

        if self.dragging:  # Если зажата ЛКМ → изменяем масштаб
            scale_step = 0.1
            self.scale_factor = max(0.2, min(3.0, self.scale_factor + delta * scale_step))
            
            # Новый размер
            new_width = int(self.image.width() * self.scale_factor)
            new_height = int(self.image.height() * self.scale_factor)

            self.resize(new_width, new_height)
            self.image_label.resize(new_width, new_height)
        
        elif self.changing_opacity:  # Если зажата ПКМ → изменяем прозрачность
            self.opacity = max(10, min(255, self.opacity + int(delta * 15)))
            self.update_image_opacity()

    def dragEnterEvent(self, event):
        """Разрешает перетаскивание изображений"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Обрабатывает перетаскивание изображения"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path) and file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                self.load_image(file_path)

    def load_image(self, file_path):
        """Загружает изображение"""
        self.image = QPixmap(file_path)
        self.image_label.setPixmap(self.image)
        self.image_label.resize(self.image.size())
        self.resize(self.image.size())
        self.drag_zone.hide()  # Скрываем зону перетаскивания


app = QApplication(sys.argv)
window = TransparentWindow()
window.show()
sys.exit(app.exec())
