from PyQt6.QtWidgets import QGridLayout, QLabel, QWidget, QFileDialog
from PyQt6.QtGui import QPixmap, QColor, QImage
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt


class QGrid(QGridLayout):
    def __init__(self):
        super().__init__()
        self.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

    def addWidget(self, widget, row, column, rowSpan=1, columnSpan=1):
        super().addWidget(widget, row, column, rowSpan, columnSpan)
        self.setAlignment(widget, Qt.AlignmentFlag.AlignCenter)


class QObjects:
    @staticmethod
    def canvas(width: int, height: int) -> QLabel:
        img = QLabel()
        image = QImage(width, height, QImage.Format.Format_RGB32)
        image.fill(QColor(0, 0, 0).rgb())
        img.setPixmap(QPixmap(image))
        return img

    @staticmethod
    def label(text: str) -> QLabel:
        l = QLabel()
        l.setText(text)
        return l


class QDialogs(QWidget):
    def open_path(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)"
        )
        return filename

    def save_path(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "image.bmp", "Image Files (*.png *.jpg *.bmp)"
        )
        return filename
