import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QAction
from PyQt5.QtGui import (
    QIcon,
    QPixmap,
    QImage,
    QFont,
    QGuiApplication,
    QMouseEvent,
    QColor,
)
from PyQt5.QtCore import Qt
from modules.filters import Filters
from modules.functions import gray_from_rgb
from modules.statemanager import StateManager, CanvaState
from modules.qt_override import QGrid, QObjects, QDialogs, QChildWindow

# Override the default QWidget to automatically center the elements


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Digital Image Processing"
        self.w, self.h = 750, 330
        f = None
        self.input_canvas: QLabel = QLabel()  # Canvas
        self.output_canvas: QLabel = QLabel()  # Canvas
        self.initUI()

    def set_window_props(self) -> None:
        self.setWindowTitle(self.title)
        # self.setFixedSize(self.w, self.h)
        self.setGeometry(0, 0, self.w, self.h)
        qt_rectangle = self.frameGeometry()
        center_point = QGuiApplication.primaryScreen().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())
        self.setWindowIcon(QIcon("assets/icon.png"))

    def initUI(self) -> None:
        self.set_window_props()
        self.state = StateManager(max_states=64)
        self.menubar()
        self.main_grid()

    def menubar(self):
        mb = self.menuBar()
        mb.setNativeMenuBar(False)
        self.fileMenu(mb.addMenu("File"))
        self.editMenu(mb.addMenu("Edit"))
        self.filtersMenu(mb.addMenu("Filters"))
        self.toolsMenu(mb.addMenu("Tools"))
        self.setMenuBar(mb)

    def main_grid(self):
        grid = QGrid()

        # Input canvas (left)
        input_label, self.input_canvas = self.create_canvas("Entrada")
        self.input_canvas.setMouseTracking(True)
        self.input_canvas.mouseMoveEvent = self.display_pixel_info
        grid.addWidget(input_label, 0, 0)
        grid.addWidget(self.input_canvas, 1, 0)

        # Button to apply the changes made on the output canvas
        copy_btn = QObjects.button(
            name="<",
            func=self.apply_output,
            shortcut="CTRL+P",
            tooltip="Aplicar Alterações",
        )
        copy_btn.setFont(QFont("Monospace", 28))
        copy_btn.setStyleSheet("font-weight: bold;")
        grid.addWidget(copy_btn, 1, 1)

        # Output canvas (right)
        output_label, self.output_canvas = self.create_canvas("Saída")
        grid.addWidget(output_label, 0, 2)
        grid.addWidget(self.output_canvas, 1, 2)

        self.pixel_color_label = QLabel()
        self.pixel_color_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pixel_color_label.setText(f"(0, 0)")
        self.pixel_color_label.setStyleSheet(
            "background-color: black;\
            color: white; \
            border: 1px solid transparent; \
            border-radius: 10px;"
        )
        self.pixel_color_label.setFixedSize(120, 60)

        grid.addWidget(self.pixel_color_label, 2, 1)

        # Initial state
        # self.reload_input_canvas()
        # self.reload_output_canvas()

        grid.setRowStretch(3, 1)

        self.show_grid_on_window(self, grid)

    def show_histogram(self) -> None:
        """
        Plot the histogram of an image.
        """
        import matplotlib.pyplot as plt
        import numpy as np

        f = Filters(self.input_image)
        gray = f.grayscale().get_canvas()
        # Maximum value of the histogram is 1. 0 is the minimum value
        hist, bins = np.histogram(gray, bins=256, range=(0, 255))
        hist = hist / np.max(hist)
        # Plot the histogram as a bar chart
        plt.bar(bins[:-1], hist, width=2, color="black")
        plt.title("Histograma")
        plt.show()

    def _add_channels_to_grid(self, grid: QGrid) -> None:
        f = Filters(self.input_canvas.pixmap().toImage())
        colors = ["red", "green", "blue"]
        for i, color in enumerate(colors):
            l, c = self.create_canvas(colors[i], 320, 240)
            l.setStyleSheet(f"background-color: {color};")
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l.setFixedWidth(int(self.w * 1.3 / 3))
            c.setPixmap(f.get_channel(color))
            c.setContentsMargins(0, 0, 0, 0)
            grid.addWidget(l, 0, i)
            grid.addWidget(c, 1, i)

    def show_channels(self) -> None:
        """
        Show the channel of an image.
        """
        grid = QGrid()
        self._add_channels_to_grid(grid)
        grid.setRowStretch(2, 1)
        w, h = int(self.w * 1.25), int(self.h * 0.8)
        child = QChildWindow(self, "Channels", w, h)
        self.show_grid_on_window(child, grid)

    def show_grid_on_window(self, window: QMainWindow, grid: QGrid) -> None:
        """
        Set the layout of a window.
        """
        widget = QWidget()
        widget.setLayout(grid)
        window.setCentralWidget(widget)
        window.show()

    def fileMenu(self, fileMenu):
        options = (
            ("Open", self.open_image, "CTRL+O", "Open an image"),
            ("Save", self.save_image, "CTRL+S", "Save the image"),
            ("Exit", self.close, "CTRL+Q", "Exit the application"),
        )
        for (name, fn, hot, tip) in options:
            fileMenu.addAction(self.add_submenu(name, fn, hot, tip))

    def editMenu(self, editMenu):
        commands = {
            "Undo": (self.undo, "Ctrl+Z"),
            "Redo": (self.redo, "Ctrl+Shift+Z"),
        }
        for name, (func, shortcut) in commands.items():
            m = self.add_submenu(name, func, shortcut)
            editMenu.addAction(m)

    def toolsMenu(self, toolsMenu):
        commands = {
            "Histogram": (self.show_histogram, "Ctrl+H"),
            "Channels": (self.show_channels, "Ctrl+C"),
        }
        for name, (func, shortcut) in commands.items():
            m = self.add_submenu(name, func, shortcut)
            toolsMenu.addAction(m)

    def filtersMenu(self, filtersMenu):
        f = lambda filter: self.apply_filter(filter)
        filters = {
            "Grayscale": lambda: f("grayscale"),
            "Equalize": lambda: f("equalize"),
            "Negative": lambda: f("negative"),
            "Binarize": lambda: f("binarize"),
            "Salt and Pepper": lambda: f("salt_and_pepper"),
            "Gaussian Blur": lambda: f("blur"),
            "Blur Median": lambda: f("blur_median"),
            "Dynamic Compression": lambda: f("dynamic_compression"),
            "Sobel": lambda: f("sobel"),
            "Laplacian": lambda: f("laplacian"),
        }

        for i, (name, filter) in enumerate(filters.items()):
            shortcut = f"F{i+1}" if i < 12 else f"Ctrl+{i+1}"
            tooltip = f"Apply {name} filter"
            filtersMenu.addAction(self.add_submenu(name, filter, shortcut, tooltip))

    def apply_filter(self, filter: str) -> None:
        # Create image from QPixmap
        f = Filters(QImage(self.input_canvas.pixmap()))
        output = None
        match filter:
            case "grayscale":
                output = f.grayscale()
            case "equalize":
                output = f.equalize()
            case "negative":
                output = f.negative()
            case "binarize":
                output = f.binarize()
            case "blur":
                output = f.blur()
            case "blur_median":
                output = f.blur_median()
            case "salt_and_pepper":
                output = f.salt_and_pepper()
            case "dynamic_compression":
                output = f.dynamic_compression()
            case "sobel":
                output = f.sobel()
            case "laplacian":
                output = f.laplace()
            case _:
                pass
        if output:
            self.update_output_canvas(output)

    def apply_output(self):
        self.input_canvas.setPixmap(self.output_canvas.pixmap())

    def update_output_canvas(self, qimage: QImage):
        self.output_canvas.setPixmap(QPixmap.fromImage(qimage))

    def display_pixel_info(self, event: QMouseEvent) -> QColor:
        """
        Get the color of the pixel under the mouse cursor.
        """
        x, y, c = self.pixel_info(event)
        self.pixel_color_label.setText(f"({x}, {y})")
        fg = "white" if gray_from_rgb(*c) < 127 else "black"
        self.pixel_color_label.setStyleSheet(
            f"background-color: rgb({c[0]}, {c[1]}, {c[2]}); \
              color: {fg}; \
              border: 1px solid transparent; \
              border-radius: 10px;"
        )

    def pixel_info(self, event: QMouseEvent) -> None:
        x, y = event.x(), event.y()
        image = self.input_canvas.pixmap().toImage()
        color = QColor(image.pixel(x, y)).getRgb()[:3]
        return x, y, color

    # Qt Manipulations
    def create_canvas(
        self, name: str = "Canvas", xscale: int = 0, yscale: int = 0
    ) -> tuple[QLabel, QLabel]:
        label = QObjects.label(name)
        label.setFont(QFont("Monospace", 16))
        canvas = QObjects.canvas(320, 240)
        if xscale != 0 and yscale != 0:
            canvas.setScaledContents(True)
            canvas.setFixedSize(xscale, yscale)
        return label, canvas

    def add_submenu(self, name=None, func=None, shortcut=None, tooltip=None):
        m = QAction(name, self)
        if func:
            m.triggered.connect(lambda: func())
        if shortcut:
            m.setShortcut(shortcut)
        if tooltip:
            m.setToolTip(tooltip)
        return m

    # State management
    def undo(self):
        s = self.state.prev()
        if s:
            if s.input:
                self.input_canvas.setPixmap(s.input)
            if s.output:
                self.output_canvas.setPixmap(s.output)

    def redo(self):
        s = self.state.next()
        if s:
            if s.input:
                self.input_canvas.setPixmap(s.input)
            if s.output:
                self.output_canvas.setPixmap(s.output)

    # File management
    def open_image(self):
        filename = QDialogs().open_path()
        if filename:
            pixmap = QPixmap(filename).scaled(320, 240)
            self.input_canvas.setPixmap(pixmap)

    def save_image(self):
        filename = QDialogs().save_path()
        if filename:
            self.input_canvas.pixmap().save(filename)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
