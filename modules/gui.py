import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QMainWindow,
)
from PyQt6.QtGui import (
    QIcon,
    QPixmap,
    QImage,
    QAction,
    QFont,
    QGuiApplication,
)
from PyQt6.QtCore import Qt
from classes.image import Image
from classes.adapter import Adapter
from modules.filters import Filters
from modules.statemanager import StateManager, CanvaState
from modules.qt_override import QGrid, QObjects, QDialogs, QChildWindow

# Override the default QWidget to automatically center the elements


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Digital Image Processing"
        self.w, self.h = 750, 300
        self.filters = None
        self.input_image: Image = None  # Matrix of the input image
        self.input_canvas: QLabel = QLabel()  # Canvas
        self.output_image: Image = None  # Matrix of the output image
        self.output_canvas: QLabel = QLabel()  # Canvas
        self.initUI()

    def set_window_props(self) -> None:
        self.setWindowTitle(self.title)
        self.setFixedSize(self.w, self.h)
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
        self.input_image = Adapter.QImg2Img(self.input_canvas.pixmap().toImage())
        grid.addWidget(input_label, 0, 0)
        grid.addWidget(self.input_canvas, 1, 0)

        # Button to apply the changes made on the output canvas
        copy_btn = QObjects.button(
            name="🠔",
            func=self.apply_output,
            shortcut="CTRL+P",
            tooltip="Aplicar Alterações",
        )
        copy_btn.setFont(QFont("Monospace", 28))
        copy_btn.setStyleSheet("font-weight: bold;")
        grid.addWidget(copy_btn, 1, 1)

        # Output canvas (right)
        output_label, self.output_canvas = self.create_canvas("Saída")
        self.output_image = Adapter.QImg2Img(self.output_canvas.pixmap().toImage())
        grid.addWidget(output_label, 0, 2)
        grid.addWidget(self.output_canvas, 1, 2)

        # Initial state
        self.reload_input_canvas()
        self.reload_output_canvas()

        grid.setRowStretch(3, 1)
        widget = QWidget()
        widget.setLayout(grid)
        self.setCentralWidget(widget)

    def histogram(self) -> None:
        """
        Plot the histogram of an image.
        """
        # Change figsize
        import matplotlib.pyplot as plt
        import numpy as np
        from modules.functions import gray_from_rgb

        plt.rcParams["figure.figsize"] = (2, 2)
        # plt.rcParams["figure.dpi"] = 40
        image = np.array(self.input_image.get_canvas())
        red, green, blue = image.T
        gray = [gray_from_rgb(r, g, b) for r, g, b in zip(red, green, blue)]
        # Create 256 bins (integers)
        bins = np.linspace(0, 256, 257)

        # For each bin, count the number of pixels with that value
        red_counter = {b: np.count_nonzero(red == b) for b in bins}
        green_counter = {b: np.count_nonzero(green == b) for b in bins}
        blue_counter = {b: np.count_nonzero(blue == b) for b in bins}
        gray_counter = {b: np.count_nonzero(gray == b) for b in bins}
        max_value = max(
            max(red_counter.values()),
            max(green_counter.values()),
            max(blue_counter.values()),
            max(gray_counter.values()),
        )
        # max_value = max(gray_counter.values())
        # Normalize the counts to [0, 1]. The most frequent value will be 1
        red_counter = {b: c / max_value for b, c in red_counter.items()}
        green_counter = {b: c / max_value for b, c in green_counter.items()}
        blue_counter = {b: c / max_value for b, c in blue_counter.items()}
        gray_counter = {b: c / max_value for b, c in gray_counter.items()}
        plt.subplot(2, 2, 1)
        plt.bar(bins, red_counter.values(), color="red", width=1)

        plt.ylim(0, 1.05)
        plt.subplot(2, 2, 2)
        plt.bar(bins, green_counter.values(), color="green", width=1)

        plt.ylim(0, 1.05)
        plt.subplot(2, 2, 3)
        plt.bar(bins, blue_counter.values(), color="blue", width=1)
        plt.ylim(0, 1.05)
        plt.subplot(2, 2, 4)
        plt.bar(bins, gray_counter.values(), color="gray", width=2)
        plt.ylim(0, 1.05)
        plt.show()

    def channels(self) -> None:
        """
        Plot the channels of an image.
        """
        f = Filters(self.input_image)
        images = f.channels_separation()
        # Create a subwindow
        subwindow = QMdiSubWindow()
        subwindow.setWindowTitle("Canvas")
        subwindow.setWidget(QWidget())

        subwindow.show()

    def fileMenu(self, fileMenu):
        openAct = self.add_submenu(
            "Open", self.open_image, "Ctrl+O", "Open an existing file"
        )
        saveAct = self.add_submenu(
            "Save", self.save_image, "Ctrl+S", "Save the document"
        )
        exitAct = self.add_submenu("Exit", self.close, "Ctrl+Q", "Exit the application")
        # Add actions to the menus
        fileMenu.addAction(openAct)
        fileMenu.addAction(saveAct)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAct)

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
        }

        for i, (name, filter) in enumerate(filters.items()):
            shortcut = f"F{i+1}" if i < 12 else f"Ctrl+{i+1}"
            tooltip = f"Apply {name} filter"
            filtersMenu.addAction(self.add_submenu(name, filter, shortcut, tooltip))

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
            "Histogram": (self.histogram, "Ctrl+H"),
            "Channels": (self.channels, "Ctrl+C"),
        }
        for name, (func, shortcut) in commands.items():
            m = self.add_submenu(name, func, shortcut)
            toolsMenu.addAction(m)

    def apply_filter(self, filter: str) -> Image:
        # TODO remove temp code!
        # filters1 = Filters(self.input_image)
        # img = filters1.grayscale()
        self.filters = self.filters if self.filters else Filters(self.input_image)

        output = None
        match filter:
            case "grayscale":
                output = self.filters.grayscale()
            case "equalize":
                output = self.filters.equalize()
            case "negative":
                output = self.filters.negative()
            case "binarize":
                output = self.filters.binarize()
            case "blur":
                output = self.filters.blur()
            case "blur_median":
                output = self.filters.blur_median()
            case "salt_and_pepper":
                output = self.filters.salt_and_pepper()
            case _:
                pass
        if output:
            self.update_output(output)

    # Update the canvas with the new image
    def update_output(self, image: Image):
        self.output_image = image
        self.reload_output_canvas()

    def apply_output(self):
        self.input_image = self.output_image
        self.reload_input_canvas()

    def reload_input_canvas(self):
        self.input_canvas.setPixmap(QPixmap(Adapter.Img2QImg(self.input_image)))
        self.state.add(CanvaState(inp=self.input_image))
        self.filters = Filters(self.input_image)

    def reload_output_canvas(self):
        self.output_canvas.setPixmap(QPixmap(Adapter.Img2QImg(self.output_image)))
        self.state.add(CanvaState(out=self.output_image))

    # Qt Manipulations
    def create_canvas(self, name: str = "Canvas") -> tuple[QLabel, QLabel]:
        label = QObjects().label(name)
        label.setFont(QFont("Monospace", 16))
        canvas = QObjects().canvas(320, 240)
        return label, canvas

    def create_button(
        self,
        name="Button",
        func=None,
        shortcut=None,
        tooltip=None,
    ) -> QPushButton:
        button = QPushButton(name)
        if func:
            button.clicked.connect(func)
        if shortcut:
            button.setShortcut(shortcut)
        if tooltip:
            button.setToolTip(tooltip)
        return button

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
                self.input_image = s.input
                self.reload_input_canvas()
            if s.output:
                self.output_image = s.output
                self.reload_output_canvas()

    def redo(self):
        s = self.state.next()
        if s:
            if s.input:
                self.input_image = s.input
                self.reload_input_canvas()
            if s.output:
                self.output_image = s.output
                self.reload_output_canvas()

    # File management
    def open_image(self):
        filename = QDialogs().open_path()
        if filename:
            pixmap = QPixmap(filename).scaled(320, 240)
            self.input_image = Adapter.QImg2Img(QImage(pixmap))
            self.reload_input_canvas()

    def save_image(self):
        filename = QDialogs().save_path()
        if filename:
            self.input_canvas.pixmap().save(filename)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
