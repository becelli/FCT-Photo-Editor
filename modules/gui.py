import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QMainWindow,
)
from PyQt6.QtGui import (
    QIcon,
    QPixmap,
    QImage,
    QAction,
    QColor,
    QFont,
    QGuiApplication,
)
from PyQt6.QtCore import Qt
from classes.image import Image
from classes.adapter import Adapter
from modules.filters import Filters


# Override the default QWidget to automatically center the elements
class QGrid(QGridLayout):
    def addWidget(self, widget, row, column, rowSpan=1, columnSpan=1):
        super().addWidget(widget, row, column, rowSpan, columnSpan)
        self.setAlignment(widget, Qt.AlignmentFlag.AlignCenter)


class CanvaState:
    def __init__(self, inp: Image = None, out: Image = None):
        self.input, self.output = inp, out


class StateManager:
    def __init__(self, max_states=16, initial_state=None):
        self.s = initial_state if initial_state else []
        self.cur = -1
        self.max = max_states

    def add(self, state: CanvaState):
        if len(self.s) == self.max:
            self.s.pop(0)
            self.cur -= 1

        self.cur += 1
        self.s.append(state)

    def prev(self):
        if self.cur > 0:
            changed = "input" if self.s[self.cur].input else "output"
            self.cur -= 1
            i = 0
            while self.cur - i >= 0:
                if (changed == "output" and self.s[self.cur - i].output) or (
                    changed == "input" and self.s[self.cur - i].input
                ):
                    return self.s[self.cur - i]
                i += 1
        return None

    def next(self):
        """
        Go to the next state
        """
        if self.cur < len(self.s) - 1:
            self.cur += 1
            return self.s[self.cur]
        return None


class Dialogs(QWidget):
    def open_image(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)"
        )
        return filename

    def save_image(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "", "Image Files (*.png *.jpg *.bmp)"
        )
        return filename


class QObjects:
    def canvas(self, width: int, height: int) -> QLabel:
        img = QLabel()
        image = QImage(width, height, QImage.Format.Format_RGB32)
        image.fill(QColor(255, 255, 255))

        r = 50
        for i in range(width):
            for j in range(height):
                # Draw a circle in the center of the image
                if (i - width / 2) ** 2 + (j - height / 2) ** 2 < r**2:
                    image.setPixel(i, j, QColor(255, 0, 0).rgb())

        img.setPixmap(QPixmap(image))
        return img

    def label(self, text: str) -> QLabel:
        l = QLabel()
        l.setText(text)
        return l


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Digital Image Processing"
        self.w = 750
        self.h= 300
        self.input_image: Image = None  # Matrix of the input image
        self.input_canvas: QLabel = QLabel()# Canvas
        self.output_image: Image = None  # Matrix of the output image
        self.output_canvas: QLabel = QLabel()  # Canvas
        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle(self.title)  # Título da janela
        self.setFixedSize(self.w, self.h)  # Tamanho fixo da janela
        qtRectangle = self.frameGeometry()
        centerPoint = QGuiApplication.primaryScreen().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.setWindowIcon(QIcon("assets/icon.png"))

        # State manager
        self.state = StateManager(max_states=32)

        # Application Layout
        self.menubar()
        self.main_grid()

    def menubar(self):
        mb = self.menuBar()
        mb.setNativeMenuBar(False)
        self.fileMenu(mb.addMenu("File"))
        self.editMenu(mb.addMenu("Edit"))
        self.filtersMenu(mb.addMenu("Filters"))
        self.setMenuBar(mb)

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

    def main_grid(self):
        grid = QGrid()
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)

        # Input canvas (left)
        input_label, self.input_canvas = self.create_canvas("Entrada")
        self.input_image = Adapter.QImg2Img(self.input_canvas.pixmap().toImage())
        grid.addWidget(input_label, 0, 0)
        grid.addWidget(self.input_canvas, 1, 0)

        # Apply changes to the input canvas
        copy_btn = self.create_button(
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
        self.state.add(CanvaState(inp=self.input_image))
        self.state.add(CanvaState(out=self.output_image))

        grid.setRowStretch(3, 1)
        widget = QWidget()
        widget.setLayout(grid)
        self.setCentralWidget(widget)

    def fileMenu(self, fileMenu):
        openAct = self.add_submenu(
            "Open", self.open_image_dialog, "Ctrl+O", "Open an existing file"
        )
        saveAct = self.add_submenu(
            "Save", self.save_image_dialog, "Ctrl+S", "Save the document"
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
            "Blur": lambda: f("blur"),
            "Grayscale": lambda: f("grayscale"),
            "Negative": lambda: f("negative"),
            "Binarize": lambda: f("binarize"),
            "Expand Contrast": lambda: f("expand_contrast"),
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

    def apply_filter(self, filter: str) -> Image:
        # TODO remove temp code!
        # filters1 = Filters(self.input_image)
        # img = filters1.grayscale()
        filters = Filters(self.input_image)

        output = None
        match filter:
            case "grayscale":
                output = filters.grayscale()
            case "expand_contrast":
                output = filters.expand_contrast()
            case "negative":
                output = filters.negative()
            case "binarize":
                output = filters.binarize()
            case "blur":
                output = filters.blur()
            case _:
                output = None
        if output:
            self.update_output(output)

    def update_output(self, image: Image):
        self.output_image = image
        self.reload_output_canvas()
        self.state.add(CanvaState(out=self.output_image))

    def apply_output(self):
        self.input_image = self.output_image
        self.reload_input_canvas()
        self.state.add(CanvaState(inp=self.input_image))

    def reload_input_canvas(self):
        self.input_canvas.setPixmap(QPixmap(Adapter.Img2QImg(self.input_image)))

    def reload_output_canvas(self):
        self.output_canvas.setPixmap(QPixmap(Adapter.Img2QImg(self.output_image)))

    def create_canvas(self, name: str = "Canvas") -> tuple[QLabel, QLabel]:
        label = QObjects().label(name)
        label.setFont(QFont("Monospace", 16))
        canvas = QObjects().canvas(320, 240)
        return label, canvas

    def open_image_dialog(self):
        filename = Dialogs().open_image()
        if filename:
            pixmap = QPixmap(filename).scaled(320, 240)
            self.input_image = Adapter.QImg2Img(QImage(pixmap))
            self.input_canvas.setPixmap(pixmap)

    def save_image_dialog(self):
        filename = Dialogs().save_image()
        if filename:
            self.input_canvas.pixmap().save(filename)

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

    def add_submenu(self, name=None, func=None, shortcut=None, tooltip=None):
        m = QAction(name, self)
        if func:
            m.triggered.connect(lambda: func())
        if shortcut:
            m.setShortcut(shortcut)
        if tooltip:
            m.setToolTip(tooltip)
        return m


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
