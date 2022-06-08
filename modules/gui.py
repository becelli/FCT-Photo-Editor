import sys
from PyQt5.QtWidgets import (
    QApplication,
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
)
from PyQt5.QtCore import Qt
from modules.filters import Filters
from modules.color_converter import ColorConverter
from modules.functions import (
    get_gray_from_rgb,
    get_rgb_from_color_integer,
    get_gray_from_color_integer,
    get_rgb_from_color_integer,
)
from modules.qt_override import (
    QGrid,
    QObjects,
    QDialogs,
    QChildWindow,
    display_grid_on_window,
    get_image_from_canvas,
    get_image_from_pixmap,
    get_pixmap_from_canvas,
    get_pixmap_from_image,
    put_image_on_canvas,
    put_pixmap_on_canvas,
    display_int_input_dialog,
    display_float_input_dialog,
)
import numpy as np

# Override the default QWidget to automatically center the elements


class MenuAction:
    def __init__(self, name, function, shortcut=None, tooltip=None):
        self._name = name
        self._function = function
        self._shortcut = shortcut
        self._tooltip = tooltip

    def get_values(self):
        return self._name, self._function, self._shortcut, self._tooltip

    def get_function(self):
        return self._function

    def get_name(self):
        return self._name

    def get_shortcut(self):
        return self._shortcut

    def get_tooltip(self):
        return self._tooltip


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.window_dimensions = (750, 330)
        self.input_canvas: QLabel = QLabel()
        self.output_canvas: QLabel = QLabel()
        self.initUI()

    def initUI(self) -> None:
        self._set_window_properties()
        self.display_menubar()
        self.display_main_content()

    # Main Graphical User Interface
    def _set_window_properties(self) -> None:
        self.setWindowTitle("Digital Image Processing")
        # self.setFixedSize(*self.window_dimensions)
        self._center_window()
        self.setWindowIcon(QIcon("assets/icon.png"))

    def _center_window(self) -> None:
        temporary_window = self.frameGeometry()
        center_point = QGuiApplication.primaryScreen().availableGeometry().center()
        temporary_window.moveCenter(center_point)
        self.move(temporary_window.topLeft())

    def display_menubar(self):
        menubar = self.menuBar()
        self.setMenuBar(menubar)
        self._add_menus_to_menubar(menubar)

    def display_main_content(self):
        # TODO: I don't know if i should 'clear' this code.
        # If I split this code in two, the creation of the labels and canvas
        # will be hidden to this function.
        grid = QGrid()

        input_label, self.input_canvas = self._create_canvas("Input")
        self._set_mouse_tracking_to_show_pixel_details(self.input_canvas)

        output_label, self.output_canvas = self._create_canvas("Output")
        self._set_mouse_tracking_to_show_pixel_details(self.output_canvas)

        apply_changes_button = self._create_apply_changes_button()

        self.pixel_color_label = self._create_pixel_color_and_coordinates_widget()
        self.pixel_color_label.setFont(QFont("Monospace", pointSize=10))

        grid.addWidget(input_label, 0, 0)
        grid.addWidget(self.input_canvas, 1, 0)
        grid.addWidget(apply_changes_button, 1, 1)
        grid.addWidget(output_label, 0, 2)
        grid.addWidget(self.output_canvas, 1, 2)
        grid.addWidget(self.pixel_color_label, 2, 1)

        grid.setRowStretch(3, 1)

        display_grid_on_window(self, grid)

    # Feature: Display the histogram of the input image
    def display_histogram(self) -> None:
        import matplotlib.pyplot as plt

        hist, bins = self._calculate_image_histogram()
        plt.bar(bins[:-1], hist, width=2, color="black")
        plt.title("Histograma")
        plt.show()

    def _calculate_image_histogram(self) -> tuple[np.ndarray, np.ndarray]:
        gray_image = self._get_gray_image()
        image_pixels = self._get_array_of_pixels_from_image(gray_image)
        hist, bins = np.histogram(image_pixels, bins=256, range=(0, 255))
        hist = hist / np.max(hist)  # Normalizing
        return hist, bins

    def _get_array_of_pixels_from_image(self, image: QImage) -> np.ndarray:
        width, height = image.width(), image.height()
        image_pixels_array = image.bits().asarray(width * height)
        return image_pixels_array

    def _get_gray_image(self) -> QImage:
        f = Filters(img=get_image_from_canvas(self.input_canvas))
        image: QImage = f.grayscale()
        return image

    # Feature: Display splitted color channels of the input image
    def display_color_channels(self) -> None:
        window = self._create_window_to_display_splitted_colors()
        grid = self._create_grid_with_isolated_color_channels()
        display_grid_on_window(window, grid)

    def _create_window_to_display_splitted_colors(self) -> None:
        w, h = self.window_dimensions
        w, h = int(w * 1.25), int(h * 0.8)
        return QChildWindow(self, "Channels", w, h)

    def _create_grid_with_isolated_color_channels(self) -> QGrid:
        grid = QGrid()
        self._add_channels_to_grid(grid)
        grid.setRowStretch(2, 1)
        return grid

    def _add_channels_to_grid(self, grid: QGrid) -> None:
        colors = ["red", "green", "blue"]
        for i, color in enumerate(colors):
            label, canvas = self._create_canvas(colors[i], 320, 240)
            self._insert_isolated_color_channel_into_canvas(color, canvas)
            self._get_styled_label_with_color(color, label)
            grid.addWidget(label, 0, i)
            grid.addWidget(canvas, 1, i)

    def _insert_isolated_color_channel_into_canvas(
        self, color: str, canvas: QLabel
    ) -> None:
        f = Filters(img=get_image_from_canvas(self.input_canvas))
        image: QImage = f.get_channel(color)
        put_image_on_canvas(canvas, image)

    def _get_styled_label_with_color(self, color: str, label: QLabel) -> None:
        label.setStyleSheet(f"background-color: {color};")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedWidth(int(self.window_dimensions[0] * 1.3 / 3))

    # Feature: Display pixel details when the mouse pointer is over a pixel
    def _set_mouse_tracking_to_show_pixel_details(self, element: QLabel) -> None:
        element.setMouseTracking(True)
        inform_canvas = lambda e: self._display_pixel_color_and_coordinates(e, element)
        element.mouseMoveEvent = inform_canvas

    def _create_pixel_color_and_coordinates_widget(self) -> QLabel:
        widget = QLabel()
        widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget.setFixedSize(120, 60)
        return widget

    def _display_pixel_color_and_coordinates(
        self, event: QMouseEvent, canvas: QLabel
    ) -> None:
        x, y, color = self._get_pixel_coordinates_and_color(event, canvas)
        self._paint_new_pixel_color(color)
        self._display_new_pixel_color_info(x, y, color)

    def _display_new_pixel_color_info(self, x: int, y: int, color) -> None:
        self.pixel_color_label.setText(
            f"({x }, {y})\n\n" f"rgb({color[0]}, {color[1]}, {color[2]})"
        )

    def _paint_new_pixel_color(self, color: tuple[int, int, int]) -> None:
        r, g, b = color
        text_color = self._get_contrast_color(color)
        self.pixel_color_label.setStyleSheet(
            f"background-color: rgb({r}, {g}, {b});"
            f"color: {text_color};"
            f"border: 1px solid transparent;"
            f"border-radius: 10px;"
        )

    def _get_contrast_color(self, bg_color: tuple[int, int, int]) -> str:
        return "white" if get_gray_from_rgb(*bg_color) < 128 else "black"

    def _get_pixel_coordinates_and_color(
        self, event: QMouseEvent, canvas: QLabel = None
    ) -> tuple[int, int, tuple]:
        if canvas is None:
            canvas = self.input_canvas

        x, y = event.x(), event.y()
        image = get_image_from_canvas(canvas)
        pixel_integer = image.pixel(x, y)
        color = get_rgb_from_color_integer(pixel_integer)
        return x, y, color

    # Feature: Apply filters to the input image.
    def _apply_filter_to_input_image(self, filter: str) -> None:
        f = Filters(get_image_from_canvas(self.input_canvas))
        output = None
        if filter == "grayscale":
            output = f.grayscale()
        elif filter == "equalize":
            output = f.equalize()
        elif filter == "negative":
            output = f.negative()
        elif filter == "binarize":
            output = f.binarize()
        elif filter == "mean":
            output = self._try_to_apply_mean_filter(f)
        elif filter == "median":
            output = self._try_to_apply_median_filter(f)
        elif filter == "salt_and_pepper":
            output = self._try_to_apply_salt_and_pepper_filter(f)
        elif filter == "dynamic_compression":
            output = self._try_to_apply_dynamic_compression_filter(f)
        elif filter == "sobel":
            output = f.sobel()
        elif filter == "sobel_magnitudes":
            self.display_sobel_magnitudes_filter(f)
        elif filter == "laplacian":
            output = f.laplace()
        elif filter == "limiarization":
            output = self._try_to_apply_limiarization_filter(f)
        elif filter == "resize":
            output = self._try_to_apply_resize_filter(f)
        elif filter == "normalize":
            output = f.normalize()

        else:
            pass

        if output:
            self._update_output_canvas(output)

    def _try_to_apply_mean_filter(self, filtertool: Filters) -> QImage:
        size = self._display_mean_and_median_filter_size_chooser()
        size = size + 1 if size % 2 == 0 else size
        if size >= 3:
            return filtertool.mean(size)
        return None

    def _try_to_apply_median_filter(self, filtertool: Filters) -> QImage:
        size = self._display_mean_and_median_filter_size_chooser()
        if size >= 3:
            return filtertool.median(size)
        return None

    def _display_mean_and_median_filter_size_chooser(self) -> int:
        return display_int_input_dialog("Filter size", 3, 100, 3)

    def _try_to_apply_salt_and_pepper_filter(self, filtertool: Filters) -> QImage:
        size = self._display_salt_and_pepper_filter_size_chooser()
        if size >= 1:
            return filtertool.salt_and_pepper(size)
        return None

    def _display_salt_and_pepper_filter_size_chooser(self) -> int:
        return display_int_input_dialog("Percentage of noise", 1, 100, 10)

    def _try_to_apply_dynamic_compression_filter(self, filtertool: Filters) -> QImage:
        c, gama = self._display_dynamic_compression_filter_parameters()
        if c >= 0 and gama >= 0:
            return filtertool.dynamic_compression(c, gama)
        return None

    def _display_dynamic_compression_filter_parameters(self) -> tuple[int, int]:
        constant = display_float_input_dialog("Constant c", 0, 100, 1)
        gamma = display_float_input_dialog("Gama", 0, 3, 0.8)
        return constant, gamma

    def _try_to_apply_limiarization_filter(self, filtertool: Filters) -> QImage:
        limiar = self._display_limiarization_filter_parameter()
        if limiar >= 0:
            return filtertool.limiarization(limiar)
        return None

    def _display_limiarization_filter_parameter(self) -> int:
        return display_int_input_dialog("Limiar", 0, 255, 127)

    def _try_to_apply_resize_filter(self, f: Filters) -> QImage:
        w, h = self._display_resize_filter_parameters()
        if w >= 1 and h >= 1:
            return f.resize_nearest_neighbor(w, h)
        return None

    def _display_resize_filter_parameters(self) -> tuple[int, int]:
        w = display_int_input_dialog("Width", 1, 10000, 640)
        h = display_int_input_dialog("Height", 1, 10000, 480)
        return w, h

    def display_sobel_magnitudes_filter(self, f: Filters) -> None:
        images = f.sobel_magnitudes()
        names = ["XY", "X", "Y"]
        w, h = images[0].width(), images[0].height()

        window, grid, font = self._create_sobel_magnitude_window_toolset(w, h)

        grid.setColumnStretch(0, 1)
        display_grid_on_window(window, grid)
        self._add_sobel_images_to_grid(images, names, grid, font)

        window.show()

    def _create_sobel_magnitude_window_toolset(self, w, h):
        window = QChildWindow(self, "Sobel Magnitudes", 3 * w, int(h * 1.1))
        grid = QGrid(window)
        grid.setSpacing(3)
        font = QFont("Monospace", 12)
        return window, grid, font

    def _add_sobel_images_to_grid(self, images, labels, grid, font):
        for i, image in enumerate(images):
            name = f"{labels[i]}"
            grid.addWidget(QLabel(name, font=font), 0, i)
            canvas = QLabel()
            put_image_on_canvas(canvas, image)
            grid.addWidget(canvas, 1, i)

    def _apply_output_to_input_canvas(self):
        pixmap = get_pixmap_from_canvas(self.output_canvas)
        put_pixmap_on_canvas(self.input_canvas, pixmap)

    def _update_output_canvas(self, new_image: QImage):
        put_image_on_canvas(self.output_canvas, new_image)

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
            func=self._apply_output_to_input_canvas,
            shortcut="CTRL+P",
            tooltip="Aplicar Alterações",
        )
        button.setFont(QFont("Monospace", 18))
        button.setStyleSheet("font-weight: bold; padding: 15px;")
        return button

    # Feature: Menubar functions
    def _add_submenu(self, name=None, func=None, shortcut=None, tooltip=None):
        m = QAction(name, self)
        if func:
            m.triggered.connect(lambda: func())
        if shortcut:
            m.setShortcut(shortcut)
        if tooltip:
            m.setToolTip(tooltip)
        return m

    def _add_menus_to_menubar(self, menubar) -> None:
        menus = (
            MenuAction("File", self._add_actions_to_file_menu),
            MenuAction("Filters", self._add_actions_to_filters_menu),
            MenuAction("Tools", self._add_actions_to_tools_menu),
        )
        for menu in menus:
            new_menu = menubar.addMenu(menu.get_name())
            add_submenus_to = menu.get_function()
            add_submenus_to(new_menu)

    def _add_actions_to_file_menu(self, file_menu):
        actions = (
            MenuAction("Open", self.open_image, "CTRL+O", "Open an image"),
            MenuAction("Save", self.save_image, "CTRL+S", "Save the image"),
            MenuAction("Exit", self.close, "CTRL+Q", "Exit the application"),
        )
        self._add_actions_to_generic_menu(file_menu, actions)

    def _add_actions_to_tools_menu(self, tools_menu):
        color_converter = lambda: ColorConverter(self).show_rgb_and_hsl_converter()
        # Declaring here to do not break identation.
        actions = (
            MenuAction("Histogram", self.display_histogram, "Ctrl+H"),
            MenuAction("Channels", self.display_color_channels, "Ctrl+C"),
            MenuAction("RGB to HSL", color_converter, "Ctrl+R"),
        )
        self._add_actions_to_generic_menu(tools_menu, actions)

    def _add_actions_to_filters_menu(self, filters_menu):
        f = lambda filter: self._apply_filter_to_input_image(filter)
        filters = (
            MenuAction("Grayscale", lambda: f("grayscale"), "F1"),
            MenuAction("Normalize", lambda: f("normalize"), "F2"),
            MenuAction("Equalize", lambda: f("equalize"), "F3"),
            MenuAction("Negative", lambda: f("negative"), "F4"),
            MenuAction("Binarize", lambda: f("binarize"), "F5"),
            MenuAction("Dyn. Compress.", lambda: f("dynamic_compression"), "F6"),
            MenuAction("Mean", lambda: f("mean"), "F7"),
            MenuAction("Median", lambda: f("median"), "F8"),
            MenuAction("Laplacian", lambda: f("laplacian"), "F9"),
            MenuAction("Limiarization", lambda: f("limiarization"), "F10"),
            MenuAction("Sobel", lambda: f("sobel"), "F11"),
            MenuAction("Sobel Magnitudes", lambda: f("sobel_magnitudes"), "F12"),
            MenuAction("Salt and Pepper", lambda: f("salt_and_pepper"), "Ctrl+F1"),
            MenuAction("Resize", lambda: f("resize"), "Ctrl+F2"),
        )
        self._add_actions_to_generic_menu(filters_menu, filters)

    def _add_actions_to_generic_menu(self, menu, actions: tuple[MenuAction]):
        for action in actions:
            name, func, shortcut, tooltip = action.get_values()
            act = self._add_submenu(name, func, shortcut, tooltip)
            # Adding is safe when any of the above parameters is None.
            menu.addAction(act)

    # File management
    def open_image(self):
        filename = QDialogs().get_open_path()
        if filename:
            pixmap = QPixmap(filename).scaled(320, 240)
            put_pixmap_on_canvas(self.input_canvas, pixmap)

    def save_image(self):
        filename = QDialogs().get_save_path()
        if filename:
            get_pixmap_from_canvas(self.input_canvas).save(filename)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
