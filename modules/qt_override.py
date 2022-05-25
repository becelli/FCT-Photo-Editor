from PyQt5.QtWidgets import (
    QGridLayout,
    QLabel,
    QWidget,
    QFileDialog,
    QMainWindow,
    QPushButton,
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


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
        # image.fill(QColor(0, 0, 0).rgb())
        img.setPixmap(QPixmap.fromImage(image))
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
    def get_open_path(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)"
        )
        return filename

    def get_save_path(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "image.bmp", "Image Files (*.png *.jpg *.bmp)"
        )
        return filename


def display_grid_on_window(window: QMainWindow, grid: QGrid) -> None:
    """
    Set the layout of a window.
    """
    widget = QWidget()
    widget.setLayout(grid)
    window.setCentralWidget(widget)
    window.show()


def get_image_from_canvas(canvas: QLabel) -> QImage:
    return canvas.pixmap().toImage()


def get_pixmap_from_image(image: QImage) -> QPixmap:
    return QPixmap.fromImage(image)


def get_image_from_pixmap(pixmap: QPixmap) -> QImage:
    return pixmap.toImage()


def get_pixmap_from_canvas(canvas: QLabel) -> QPixmap:
    return canvas.pixmap()


def put_pixmap_on_canvas(canvas: QLabel, pixmap: QPixmap) -> None:
    canvas.setPixmap(pixmap)


def put_image_on_canvas(canvas: QLabel, image: QImage) -> None:
    canvas.setPixmap(QPixmap.fromImage(image))
