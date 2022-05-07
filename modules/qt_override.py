from PyQt6.QtWidgets import QGridLayout, QLabel, QWidget, QFileDialog
from PyQt6.QtGui import QPixmap, QColor, QImage
from PyQt6.QtCore import Qt
from PyQtChart import QChart, QChartView, QLineSeries, QValueAxis


class QGrid(QGridLayout):
    def addWidget(self, widget, row, column, rowSpan=1, columnSpan=1):
        super().addWidget(widget, row, column, rowSpan, columnSpan)
        self.setAlignment(widget, Qt.AlignmentFlag.AlignCenter)


class QObjects:
    def canvas(self, width: int, height: int) -> QLabel:
        img = QLabel()
        image = QImage(width, height, QImage.Format.Format_RGB32)
        image.fill(QColor(0, 0, 0).rgb())
        img.setPixmap(QPixmap(image))
        return img

    def label(self, text: str) -> QLabel:
        l = QLabel()
        l.setText(text)
        return l

    def histogram(self, width: int, height: int, data: list) -> QLabel:
        img = QLabel()
        image = QImage(width, height, QImage.Format.Format_RGB32)


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
