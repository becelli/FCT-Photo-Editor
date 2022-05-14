import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QMainWindow,
    QAction,
    QPushButton,
)
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
from modules.color_converter import ColorConverter
from modules.functions import gray_from_rgb
from modules.statemanager import StateManager, CanvaState
from modules.qt_override import (
    QGrid,
    QObjects,
    QDialogs,
    QChildWindow,
    display_grid_on_window,
)
import numpy as np

# Override the default QWidget to automatically center the elements


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Digital Image Processing"
        self.w, self.h = 750, 330
        self.state = StateManager(max_states=64)
        self.input_canvas: QLabel = QLabel()
        self.output_canvas: QLabel = QLabel()
        self.initUI()

    def _set_window_props(self) -> None:
        self.setWindowTitle(self.title)
        # self.setFixedSize(self.w, self.h)
        self.setGeometry(0, 0, self.w, self.h)
        qt_rectangle = self.frameGeometry()
        center_point = QGuiApplication.primaryScreen().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())
        self.setWindowIcon(QIcon("assets/icon.png"))

    def initUI(self) -> None:
        self._set_window_props()
        self.menubar()
        self.show_main_grid()

    def menubar(self):
        mb = self.menuBar()  # Instantiate the menu bar
        self.setMenuBar(mb)
        self._append_itens_to_menu(mb)

    def show_main_grid(self):
        grid = QGrid()
        input_label, self.input_canvas = self._create_canvas("Entrada")
        self.input_canvas.setMouseTracking(True)
        self.input_canvas.mouseMoveEvent = self._display_pixel_info

        output_label, self.output_canvas = self._create_canvas("Saída")
        self.output_canvas.setMouseTracking(True)
        self.output_canvas.mouseMoveEvent = self._display_pixel_info

        apply_button = self._create_apply_changes_button()

        self.pixel_color_label = self._mouse_hover_info()

        grid.addWidget(input_label, 0, 0)  # Input canvas (left)
        grid.addWidget(self.input_canvas, 1, 0)
        grid.addWidget(apply_button, 1, 1)  # Apply changes button (center)
        grid.addWidget(output_label, 0, 2)  # Output canvas (right)
        grid.addWidget(self.output_canvas, 1, 2)
        grid.addWidget(self.pixel_color_label, 2, 1)  # Color of the pixel selected.

        grid.setRowStretch(3, 1)

        display_grid_on_window(self, grid)

    def show_histogram(self) -> None:
        import matplotlib.pyplot as plt

        hist, bins = self._calculate_histogram()
        plt.bar(bins[:-1], hist, width=2, color="black")
        plt.title("Histograma")
        plt.show()

    def show_channels(self) -> None:
        """
        Show the channel of an image.
        """
        grid = QGrid()
        self._add_channels_to_grid(grid)
        grid.setRowStretch(2, 1)

        w, h = int(self.w * 1.25), int(self.h * 0.8)
        child = QChildWindow(self, "Channels", w, h)
        display_grid_on_window(child, grid)

    # Histogram functions
    def _get_histogram_gray_image(self) -> QImage:
        f = Filters(self.input_canvas.pixmap().toImage())
        image: QImage = f.grayscale()
        return image

    def _calculate_histogram(self) -> tuple[np.ndarray, np.ndarray]:
        image = self._get_histogram_gray_image()
        bit_pixels = image.bits().asarray(image.width() * image.height())
        hist, bins = np.histogram(bit_pixels, bins=256, range=(0, 255))
        hist = hist / np.max(hist)
        return hist, bins

    # Split color channels functions
    def _add_channels_to_grid(self, grid: QGrid) -> None:
        f = Filters(self.input_canvas.pixmap().toImage())
        colors = ["red", "green", "blue"]
        for i, color in enumerate(colors):
            l, c = self._create_canvas(colors[i], 320, 240)
            self._get_channeled_images(f, color, l, c)
            grid.addWidget(l, 0, i)
            grid.addWidget(c, 1, i)

    def _get_channeled_images(
        self, f: Filters, color: str, label: QLabel, canvas: QLabel
    ) -> None:
        label.setStyleSheet(f"background-color: {color};")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedWidth(int(self.w * 1.3 / 3))
        pixmap = QPixmap.fromImage(f.get_channel(color))
        canvas.setPixmap(pixmap)
        canvas.setContentsMargins(0, 0, 0, 0)

    # Menubar functions
    def _fileMenu(self, fileMenu):
        options = (
            ("Open", self.open_image, "CTRL+O", "Open an image"),
            ("Save", self.save_image, "CTRL+S", "Save the image"),
            ("Exit", self.close, "CTRL+Q", "Exit the application"),
        )
        for (name, fn, hot, tip) in options:
            fileMenu.addAction(self._add_submenu(name, fn, hot, tip))

    def _editMenu(self, editMenu):
        commands = {
            "Undo": (self.undo, "Ctrl+Z"),
            "Redo": (self.redo, "Ctrl+Shift+Z"),
        }
        for name, (func, shortcut) in commands.items():
            m = self._add_submenu(name, func, shortcut)
            editMenu.addAction(m)

    def _toolsMenu(self, toolsMenu):
        commands = {
            "Histogram": (self.show_histogram, "Ctrl+H"),
            "Channels": (self.show_channels, "Ctrl+C"),
        }
        for name, (func, shortcut) in commands.items():
            m = self._add_submenu(name, func, shortcut)
            toolsMenu.addAction(m)

    def _filtersMenu(self, filtersMenu):
        f = lambda filter: self._apply_filter(filter)
        filters = {
            "Grayscale": lambda: f("grayscale"),
            "Equalize": lambda: f("equalize"),
            "Negative": lambda: f("negative"),
            "Binarize": lambda: f("binarize"),
            "Salt and Pepper": lambda: f("salt_and_pepper"),
            "Mean": lambda: f("mean"),
            "Median": lambda: f("median"),
            "Dynamic Compression": lambda: f("dynamic_compression"),
            "Sobel": lambda: f("sobel"),
            "Laplacian": lambda: f("laplacian"),
            # "Prewitt": lambda: f("prewitt"),
            # "Roberts": lambda: f("roberts"),
            "Limiarization": lambda: f("limiarization"),
        }

        for i, (name, filter) in enumerate(filters.items()):
            shortcut = f"F{i+1}" if i < 12 else f"Ctrl+{i+1}"
            tooltip = f"Apply {name} filter"
            filtersMenu.addAction(self._add_submenu(name, filter, shortcut, tooltip))

    # Canvas functions
    def _mouse_hover_info(self) -> QLabel:
        widget = QLabel()
        widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget.setText(f"(0, 0)")
        widget.setStyleSheet(
            "background: black; color: white; border: 1px solid transparent;  border-radius: 10px;"
        )
        widget.setFixedSize(120, 60)
        return widget

    def _display_pixel_info(self, event: QMouseEvent) -> QColor:
        """
        Get the color of the pixel under the mouse cursor.
        """
        x, y, c = self._pixel_info(event)
        self.pixel_color_label.setText(f"({x}, {y})")
        fg = "white" if gray_from_rgb(*c) < 127 else "black"

        self.pixel_color_label.setStyleSheet(
            f"background-color: rgb({c[0]}, {c[1]}, {c[2]}); \
              color: {fg}; \
              border: 1px solid transparent; \
              border-radius: 10px;"
        )

    def _pixel_info(self, event: QMouseEvent) -> None:
        x, y = event.x(), event.y()
        image = self.input_canvas.pixmap().toImage()
        color = QColor(image.pixel(x, y)).getRgb()[:3]
        return x, y, color

    def _apply_filter(self, filter: str) -> None:
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
            case "mean":
                output = f.mean(n=3)
            case "median":
                output = f.median(n=3)
            case "salt_and_pepper":
                output = f.salt_and_pepper(amount=10)
            case "dynamic_compression":
                output = f.dynamic_compression(c=1, gama=1)
            case "sobel":
                output = f.sobel()
            case "laplacian":
                output = f.laplace()
            # case "prewitt":
            #     output = f.prewitt()
            # case "roberts":
            #     output = f.roberts()
            case "limiarization":
                output = f.limiarization(t=127)
            case _:
                pass
        if output:
            self._update_output_canvas(output)

    def _apply_output(self):
        self.input_canvas.setPixmap(self.output_canvas.pixmap())

    def _update_output_canvas(self, qimage: QImage):
        pixmap = QPixmap.fromImage(qimage)
        self.output_canvas.setPixmap(pixmap)

    # Qt Manipulations
    def _create_canvas(
        self, name: str = "Canvas", xscale: int = 0, yscale: int = 0
    ) -> tuple[QLabel, QLabel]:
        label = QObjects.label(name)
        label.setFont(QFont("Monospace", 16))
        canvas = QObjects.canvas(320, 240)
        if xscale != 0 and yscale != 0:
            canvas.setScaledContents(True)
            canvas.setFixedSize(xscale, yscale)
        return label, canvas

    def _create_apply_changes_button(self) -> QPushButton:
        button = QObjects.button(
            name="Apply",
            func=self._apply_output,
            shortcut="CTRL+P",
            tooltip="Aplicar Alterações",
        )
        button.setFont(QFont("Monospace", 18))
        button.setStyleSheet("font-weight: bold; padding: 15px;")
        return button

    def _add_submenu(self, name=None, func=None, shortcut=None, tooltip=None):
        m = QAction(name, self)
        if func:
            m.triggered.connect(lambda: func())
        if shortcut:
            m.setShortcut(shortcut)
        if tooltip:
            m.setToolTip(tooltip)
        return m

    def _append_itens_to_menu(self, menu) -> None:
        menus = {
            "File": self._fileMenu,
            "Edit": self._editMenu,
            "Filters": self._filtersMenu,
            "Tools": self._toolsMenu,
        }
        for menu_name, menu_function in menus.items():
            menu_function(menu.addMenu(menu_name))

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
