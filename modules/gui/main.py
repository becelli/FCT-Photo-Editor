from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton
from PyQt5.QtGui import QIcon, QPixmap, QImage, QFont, QGuiApplication, QMouseEvent
from PyQt5.QtCore import Qt

from modules.filters import Filters
from modules.gui.color_converter import ColorConverter
import modules.colors_adapter as c_adpt
import modules.gui.qt_override as qto
import modules.gui.frequencyd as freqd
import modules.gui.histogram as hist


class MenuAction:
    def __init__(self, name, function, shortcut=None, tooltip=None):
        self.name = name
        self.function = function
        self.shortcut = shortcut
        self.tooltip = tooltip

    def get_values(self):
        return self.name, self.function, self.shortcut, self.tooltip

    def get_function(self):
        return self.function

    def get_name(self):
        return self.name

    def get_shortcut(self):
        return self.shortcut

    def get_tooltip(self):
        return self.tooltip


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.window_dimensions = (750, 330)
        self.input_canvas: QLabel = QLabel()
        self.output_canvas: QLabel = QLabel()
        self.initUI()

    def initUI(self) -> None:
        self.set_window_properties()
        self.display_menubar()
        self.display_main_content()

    # Main Graphical User Interface
    def set_window_properties(self) -> None:
        self.setWindowTitle("Digital Image Processing")
        # self.setFixedSize(*self.window_dimensions)
        self.center_window()
        self.setWindowIcon(QIcon("assets/icon.png"))

    def center_window(self) -> None:
        temporary_window = self.frameGeometry()
        center_point = QGuiApplication.primaryScreen().availableGeometry().center()
        temporary_window.moveCenter(center_point)
        self.move(temporary_window.topLeft())

    def display_menubar(self):
        menubar = self.menuBar()
        self.setMenuBar(menubar)
        self.add_menus_to_menubar(menubar)

    def display_main_content(self):
        grid = qto.QGrid()

        input_label, self.input_canvas = qto.create_label_and_canvas("Input")
        self.set_mouse_tracking_to_show_pixel_details(self.input_canvas)

        output_label, self.output_canvas = qto.create_label_and_canvas("Output")
        self.set_mouse_tracking_to_show_pixel_details(self.output_canvas)

        apply_changes_button = self.create_apply_changes_button()

        self.pixel_color_label = self.create_pixel_color_and_coordinates_widget()
        self.pixel_color_label.setFont(QFont("Monospace", pointSize=10))

        grid.addWidget(input_label, 0, 0)
        grid.addWidget(self.input_canvas, 1, 0)
        grid.addWidget(apply_changes_button, 1, 1)
        grid.addWidget(output_label, 0, 2)
        grid.addWidget(self.output_canvas, 1, 2)
        grid.addWidget(self.pixel_color_label, 2, 1)

        grid.setRowStretch(3, 1)

        qto.display_grid_on_window(self, grid)

    # Feature: Display the histogram of the input image

    # Feature: Display splitted color channels of the input image
    def display_color_channels(self) -> None:
        window = self.create_window_to_display_splitted_colors()
        grid = self.create_grid_with_isolated_color_channels()
        qto.display_grid_on_window(window, grid)

    def create_window_to_display_splitted_colors(self) -> None:
        w, h = self.window_dimensions
        w, h = int(w * 1.25), int(h * 0.8)
        return qto.QChildWindow(self, "Channels", w, h)

    def create_grid_with_isolated_color_channels(self) -> qto.QGrid:
        grid = qto.QGrid()
        self.add_channels_to_grid(grid)
        grid.setRowStretch(2, 1)
        return grid

    def add_channels_to_grid(self, grid: qto.QGrid) -> None:
        colors = ["red", "green", "blue"]
        for i, color in enumerate(colors):
            label, canvas = qto.create_label_and_canvas(colors[i], 320, 240)
            self.insert_isolated_color_channel_into_canvas(color, canvas)
            self.get_styled_label_with_color(color, label)
            grid.addWidget(label, 0, i)
            grid.addWidget(canvas, 1, i)

    def insert_isolated_color_channel_into_canvas(
        self, color: str, canvas: QLabel
    ) -> None:
        f = Filters(img=qto.get_image_from_canvas(self.input_canvas))
        image: QImage = f.split_color_channel(color)
        qto.put_image_on_canvas(canvas, image)

    def get_styled_label_with_color(self, color: str, label: QLabel) -> None:
        label.setStyleSheet(f"background-color: {color};")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedWidth(int(self.window_dimensions[0] * 1.3 / 3))

    # Feature: Display pixel details when the mouse pointer is over a pixel
    def set_mouse_tracking_to_show_pixel_details(self, element: QLabel) -> None:
        element.setMouseTracking(True)
        inform_canvas = lambda e: self.display_pixel_color_and_coordinates(e, element)
        element.mouseMoveEvent = inform_canvas

    def create_pixel_color_and_coordinates_widget(self) -> QLabel:
        widget = QLabel()
        widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget.setFixedSize(120, 60)
        return widget

    def display_pixel_color_and_coordinates(
        self, event: QMouseEvent, canvas: QLabel
    ) -> None:
        x, y, color = self.get_pixel_coordinates_and_color(event, canvas)
        self.paint_new_pixel_color(color)
        self.display_new_pixel_color_info(x, y, color)

    def display_new_pixel_color_info(self, x: int, y: int, color) -> None:
        self.pixel_color_label.setText(
            f"({x }, {y})\n\n" f"rgb({color[0]}, {color[1]}, {color[2]})"
        )

    def paint_new_pixel_color(self, color: tuple[int, int, int]) -> None:
        r, g, b = color
        text_color = self.get_contrast_color(color)
        self.pixel_color_label.setStyleSheet(
            f"background-color: rgb({r}, {g}, {b});"
            f"color: {text_color};"
            f"border: 1px solid transparent;"
            f"border-radius: 10px;"
        )

    def get_contrast_color(self, bg_color: tuple[int, int, int]) -> str:
        return "white" if c_adpt.get_gray_from_rgb(*bg_color) < 128 else "black"

    def get_pixel_coordinates_and_color(
        self, event: QMouseEvent, canvas: QLabel = None
    ) -> tuple[int, int, tuple]:
        if canvas is None:
            canvas = self.input_canvas

        x, y = event.x(), event.y()
        image = qto.get_image_from_canvas(canvas)
        pixel_integer = image.pixel(x, y)
        color = c_adpt.get_rgb_from_color_integer(pixel_integer)
        return x, y, color

    # fmt: off
    # Feature: Apply filters to the input image.
    def apply_filter_to_input_image(self, filter: str) -> None:
        all_filters = {
            # No parameters
            "Grayscale": lambda: f.grayscale(),
            "Equalize": lambda: f.equalize(),
            "Negative": lambda: f.negative(),
            "Sobel": lambda: f.sobel(),
            "Laplacian": lambda: f.laplace(),
            "Normalize": lambda: f.normalize(),
            "Laplacian of Gaussian": lambda: f.gaussian_laplacian(),
            "Colorize from Gray": lambda: f.gray_to_color_scale(),
            "Noise Reduction Max": lambda: f.noise_reduction_max(),
            "Noise Reduction Min": lambda: f.noise_reduction_min(),
            "Noise Reduction Midpoint": lambda: f.noise_reduction_midpoint(),
            "OTSU Binarize": lambda: f.otsu_binarize(),
            "OTSU Limiarize": lambda: f.otsu_limiarize(),
            "HSL Equalize": lambda: f.hsl_equalize(),

            "Binarize": lambda: self.try_to_binarize_image(f),
            "Mean": lambda: self.try_to_apply_mean_filter(f),
            "Median": lambda: self.try_to_apply_median_filter(f),
            "Salt and Pepper": lambda: self.try_to_apply_salt_and_pepper_filter(f),
            "Dynamic Compression": lambda: self.try_to_apply_dynamic_compression_filter(f),
            "Sobel Magnitudes": lambda: self.display_sobel_magnitudes_filter(f),
            "Limiarize": lambda: self.try_to_apply_limiarization_filter(f),
            "Resize": lambda: self.try_to_apply_resize_filter(f),
        }
        f = Filters(qto.get_image_from_canvas(self.input_canvas))
        if filter in all_filters:
            output = all_filters[filter]()
            self.update_output_canvas(output)
    # fmt: on
    def try_to_apply_mean_filter(self, filtertool: Filters) -> QImage:
        size = self.display_mean_and_median_filter_size_chooser()
        size = size + 1 if size % 2 == 0 else size
        if size >= 3:
            return filtertool.mean(size)
        return None

    def try_to_apply_median_filter(self, filtertool: Filters) -> QImage:
        size = self.display_mean_and_median_filter_size_chooser()
        if size >= 3:
            return filtertool.median(size)
        return None

    def display_mean_and_median_filter_size_chooser(self) -> int:
        return qto.display_int_input_dialog("Filter size", 3, 100, 3)

    def try_to_apply_salt_and_pepper_filter(self, filtertool: Filters) -> QImage:
        size = self.display_salt_and_pepper_filter_size_chooser()
        if size >= 1:
            return filtertool.salt_and_pepper(size)
        return None

    def display_salt_and_pepper_filter_size_chooser(self) -> int:
        return qto.display_int_input_dialog("Percentage of noise", 1, 100, 10)

    def try_to_apply_dynamic_compression_filter(self, filtertool: Filters) -> QImage:
        c, gama = self.display_dynamic_compression_filter_parameters()
        if c >= 0 and gama >= 0:
            return filtertool.dynamic_compression(c, gama)
        return None

    def display_dynamic_compression_filter_parameters(self) -> tuple[int, int]:
        constant = qto.display_float_input_dialog("Constant c", 0, 100, 1)
        gamma = qto.display_float_input_dialog("Gama", 0, 3, 0.8)
        return constant, gamma

    def try_to_apply_limiarization_filter(self, filtertool: Filters) -> QImage:
        limiar = self.display_limiarization_filter_parameter()
        if limiar >= 0:
            return filtertool.limiarize(limiar)
        return None

    def try_to_binarize_image(self, filtertool: Filters) -> QImage:
        limiar = self.display_limiarization_filter_parameter()
        if limiar >= 0:
            return filtertool.binarize(limiar)
        return None

    def display_limiarization_filter_parameter(self) -> int:
        return qto.display_int_input_dialog("Limiar", 0, 255, 127)

    def try_to_apply_resize_filter(self, f: Filters) -> QImage:
        w, h = self.display_resize_filter_parameters()
        if w > 0 and h > 0:
            return f.resize_nearest_neighbor(w, h)
        return None

    def display_resize_filter_parameters(self) -> tuple[int, int]:
        w = qto.display_int_input_dialog("Width", 1, 10000, 512)
        if w > 0:
            h = qto.display_int_input_dialog("Height", 1, 10000, 512)
            return w, h
        return -1, -1

    def display_sobel_magnitudes_filter(self, f: Filters) -> None:
        images = f.sobel_magnitudes()
        names = ["XY", "X", "Y"]
        w, h = images[0].width(), images[0].height()

        window, grid, font = self.create_sobel_magnitude_window_toolset(w, h)

        grid.setColumnStretch(0, 1)
        qto.display_grid_on_window(window, grid)
        self.add_sobel_images_to_grid(images, names, grid, font)

        window.show()

    def create_sobel_magnitude_window_toolset(self, w, h):
        window = qto.QChildWindow(self, "Sobel Magnitudes", 3 * w, int(h * 1.1))
        grid = qto.QGrid(window)
        grid.setSpacing(3)
        font = QFont("Monospace", 12)
        return window, grid, font

    def add_sobel_images_to_grid(self, images, labels, grid, font):
        for i, image in enumerate(images):
            name = f"{labels[i]}"
            grid.addWidget(QLabel(name, font=font), 0, i)
            canvas = QLabel()
            qto.put_image_on_canvas(canvas, image)
            grid.addWidget(canvas, 1, i)

    def apply_output_to_input_canvas(self):
        pixmap = qto.get_pixmap_from_canvas(self.output_canvas)
        qto.put_pixmap_on_canvas(self.input_canvas, pixmap)

    def update_output_canvas(self, new_image: QImage):
        if new_image is not None:
            qto.put_image_on_canvas(self.output_canvas, new_image)

    def create_apply_changes_button(self) -> QPushButton:
        button = qto.QObjects.button(
            name="Apply",
            func=self.apply_output_to_input_canvas,
            shortcut="CTRL+P",
            tooltip="Aplicar Alterações",
        )
        button.setFont(QFont("Monospace", 18))
        button.setStyleSheet("font-weight: bold; padding: 15px;")
        return button

    def add_menus_to_menubar(self, menubar) -> None:
        menus = (
            MenuAction("File", self.add_actions_to_file_menu),
            MenuAction("Filters", self.add_actions_to_filters_menu),
            MenuAction("Convolutions", self.add_actions_to_convolutions_menu),
            MenuAction("Tools", self.add_actions_to_tools_menu),
        )
        for menu in menus:
            new_menu = menubar.addMenu(menu.get_name())
            add_submenus_to = menu.get_function()
            add_submenus_to(new_menu)

    def add_actions_to_file_menu(self, file_menu):
        actions = (
            MenuAction("Open", self.open_image, "CTRL+O", "Open an image"),
            MenuAction("Save", self.save_image, "CTRL+S", "Save the image"),
            MenuAction("Exit", self.close, "CTRL+Q", "Exit the application"),
        )
        self.add_actions_to_generic_menu(file_menu, actions)

    # fmt: off
    def add_actions_to_tools_menu(self, tools_menu):
        f = lambda filter: self.apply_filter_to_input_image(filter)
        actions = (
            MenuAction("Channels", self.display_color_channels),
            MenuAction("Resize", lambda: f("Resize"), "Ctrl+R"),
            MenuAction("Colorize Gray", lambda: f("Colorize from Gray"), "Ctrl+G"),
            MenuAction("Frequency Domain", lambda: freqd.FreqDomain(self, self.input_canvas, self.output_canvas), "Ctrl+F"),
            MenuAction("Sobel Magnitudes", lambda: f("Sobel Magnitudes")),
            MenuAction("Color Converter", lambda: ColorConverter(self)),
            MenuAction("Histogram", lambda: hist.display_histogram(self, self.input_canvas), "Ctrl+H"),
        )
        self.add_actions_to_generic_menu(tools_menu, actions)

    def add_actions_to_filters_menu(self, filters_menu):
        f = lambda filter: self.apply_filter_to_input_image(filter)
        filters = (
            MenuAction("Grayscale", lambda: f("Grayscale"), "F1"),
            MenuAction("Normalize", lambda: f("Normalize"), "F2"),
            MenuAction("Equalize", lambda: f("Equalize"), "F3"),
            MenuAction("Negative", lambda: f("Negative"), "F4"),
            MenuAction("Binarize", lambda: f("Binarize"), "F5"),
            MenuAction("Limiarize", lambda: f("Limiarize"), "F6"),
            MenuAction("OTSU Binarize", lambda: f("OTSU Binarize"), "F7"),
            MenuAction("OTSU Limiarize", lambda: f("OTSU Limiarize"), "F8"),
            MenuAction("Dyn. Compress.", lambda: f("Dynamic Compression"), "F9"),
            MenuAction("Noise Reduction Max", lambda: f("Noise Reduction Max"), "F10"),
            MenuAction("Noise Reduction Min", lambda: f("Noise Reduction Min"), "F11"),
            MenuAction("Noise Reduction Midpoint", lambda: f("Noise Reduction Midpoint"), "F12"),
            MenuAction("HSL Equalize", lambda: f("HSL Equalize"), "Ctrl+F1"),
            MenuAction("Salt and Pepper", lambda: f("Salt and Pepper"), "Ctrl+F2"),
        )
        self.add_actions_to_generic_menu(filters_menu, filters)

    def add_actions_to_convolutions_menu(self, convolutions_menu):
        f = lambda conv: self.apply_filter_to_input_image(conv)
        convolutions = (
            MenuAction("Mean", lambda: f("Mean"), "Alt+1"),
            MenuAction("Median", lambda: f("Median"), "Alt+2"),
            MenuAction("Sobel", lambda: f("Sobel"), "Alt+3"),
            MenuAction("Laplacian", lambda: f("Laplacian"), "Alt+4"),
            MenuAction("Laplacian of Gaussian", lambda: f("Laplacian of Gaussian"), "Alt+5"),
        )
        self.add_actions_to_generic_menu(convolutions_menu, convolutions)

    # fmt: on
    def add_actions_to_generic_menu(self, menu, actions: tuple[MenuAction]):
        for action in actions:
            name, func, shortcut, tooltip = action.get_values()
            act = qto.add_submenu(self, name, func, shortcut, tooltip)
            menu.addAction(act)

    # File management
    def open_image(self):
        filename = qto.QDialogs().get_open_path()
        if filename:
            pixmap = QPixmap(filename)
            qto.put_pixmap_on_canvas(self.input_canvas, pixmap)

    def save_image(self):
        filename = qto.QDialogs().get_save_path()
        if filename:
            qto.get_pixmap_from_canvas(self.input_canvas).save(filename)


def main():
    from sys import argv, exit

    app = QApplication(argv)
    window = MainWindow()
    window.show()
    exit(app.exec())
