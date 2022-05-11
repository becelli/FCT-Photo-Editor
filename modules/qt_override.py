from PyQt6.QtWidgets import (
    QGridLayout,
    QLabel,
    QWidget,
    QFileDialog,
    QMainWindow,
    QPushButton,
)
from PyQt6.QtGui import QPixmap, QColor, QImage, QGuiApplication
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

    @staticmethod
    def button(
        name="Button",
        func=None,
        shortcut=None,
        tooltip=None,
    ) -> QPushButton:

        btn = QPushButton(name)
        if func:
            btn.clicked.connect(func)
        if shortcut:
            btn.setShortcut(shortcut)
        if tooltip:
            btn.setToolTip(tooltip)
        return btn


class QChildWindow(QMainWindow):
    def __init__(self, parent: QMainWindow, title: str, width: int, height: int):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(width, height)


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
