from PyQt5.QtWidgets import QLabel, QLineEdit
from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtCore import Qt
from modules.qt_override import QGrid, QChildWindow, display_grid_on_window


class ColorConverter:
    def __init__(self, parent):
        self.parent = parent
        self.r_c, self.g_c, self.b_c = 255, 255, 255
        self.h_c, self.s_c, self.l_c = 239, 240, 240

    def _convert_rgb_to_hsl(self, r: int, g: int, b: int) -> None:
        """
        Convert to microsoft's hsl
        where h is 0-239, s is 0-240, l is 0-240
        and the rgb values are 0-255
        """
        r, g, b = r / 255, g / 255, b / 255
        mx = max(r, g, b)
        mn = min(r, g, b)
        h, s, l = 0, 0, (mx + mn) / 2

        d = mx - mn
        if d == 0:
            h = 0
        elif mx == r:
            h = ((g - b) / d) % 6
        elif mx == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4

        h = h * 40

        if h < 0:
            h += 240
        s = d / (1 - abs(2 * l - 1)) if d != 0 else 0
        self.h_c = h
        self.s_c = s * 240
        self.l_c = l * 240

    def _convert_hsl_to_rgb(self, h: int, s: int, l: int) -> None:
        """
        Convert from HSL to RGB
        where h is 0-239, s is 0-240, l is 0-240
        and the rgb values are 0-255
        """
        r, g, b = 0, 0, 0
        h, s, l = h, s / 240, l / 240

        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 40) % 2 - 1))
        m = l - c / 2

        if h < 40:
            r, g, b = c, x, 0
        elif h < 80:
            r, g, b = x, c, 0
        elif h < 120:
            r, g, b = 0, c, x
        elif h < 160:
            r, g, b = 0, x, c
        elif h < 200:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        r, g, b = (r + m) * 255, (g + m) * 255, (b + m) * 255
        self.r_c, self.g_c, self.b_c = r, g, b

    def _update_rgb_input(self, input_field: QLineEdit, color: str) -> None:
        try:
            value = int(input_field.text())
            if value < 0:
                value = 0
            elif value > 255:
                value = 255
            input_field.setText(str(value))
            setattr(self, f"{color}_c", value)
        except ValueError:
            pass

        self.color_preview.setStyleSheet(
            f"background-color: rgb({int(self.r_c)}, {int(self.g_c)}, {int(self.b_c)});"
        )
        self.rgb_to_hsl()

    def _update_hsl_input(self, input_field: QLineEdit, color: str) -> None:
        try:
            value = int(input_field.text())
            if color == "h":
                if value < 0:
                    value = 0
                elif value > 239:
                    value = 239
            elif color == "s" or color == "l":
                if value < 0:
                    value = 0
                elif value > 240:
                    value = 240
            input_field.setText(str(value))
            setattr(self, f"{color}_c", value)
        except ValueError:
            pass
        self.hsl_to_rgb()

    def show_rgb_and_hsl_converter(self) -> None:
        window = QChildWindow(self.parent, "RGB -> HSL", 270, 360)
        grid = QGrid()
        grid.setSpacing(10)

        rgb_label = QLabel("RGB")
        rgb_label.setFont(QFont("Arial", 12))
        rgb_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(rgb_label, 0, 0, 1, 2)

        r_label = QLabel("R")
        r_label.setFont(QFont("Arial", 12))
        r_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(r_label, 1, 0)

        self.r_input = QLineEdit()
        self.r_input.setFont(QFont("Arial", 12))
        self.r_input.setAlignment(Qt.AlignCenter)
        self.r_input.setValidator(QDoubleValidator(0, 255, 0))
        self.r_input.setText(str(self.r_c))
        self.r_input.textEdited.connect(
            lambda: self._update_rgb_input(self.r_input, "r")
        )
        grid.addWidget(self.r_input, 1, 1)

        g_label = QLabel("G")
        g_label.setFont(QFont("Arial", 12))
        g_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(g_label, 2, 0)

        self.g_input = QLineEdit()
        self.g_input.setFont(QFont("Arial", 12))
        self.g_input.setAlignment(Qt.AlignCenter)
        self.g_input.setValidator(QDoubleValidator(0, 255, 0))
        self.g_input.setText(str(self.g_c))
        self.g_input.textEdited.connect(
            lambda: self._update_rgb_input(self.g_input, "g")
        )
        grid.addWidget(self.g_input, 2, 1)

        b_label = QLabel("B")
        b_label.setFont(QFont("Arial", 12))
        b_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(b_label, 3, 0)

        self.b_input = QLineEdit()
        self.b_input.setFont(QFont("Arial", 12))
        self.b_input.setAlignment(Qt.AlignCenter)
        self.b_input.setValidator(QDoubleValidator(0, 255, 0))
        self.b_input.setText(str(self.b_c))
        self.b_input.textEdited.connect(
            lambda: self._update_rgb_input(self.b_input, "b")
        )
        grid.addWidget(self.b_input, 3, 1)

        hsl_label = QLabel("HSL")
        hsl_label.setFont(QFont("Arial", 12))
        hsl_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(hsl_label, 4, 0, 1, 2)

        h_label = QLabel("H")
        h_label.setFont(QFont("Arial", 12))
        h_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(h_label, 5, 0)

        self.h_input = QLineEdit()
        self.h_input.setFont(QFont("Arial", 12))
        self.h_input.setAlignment(Qt.AlignCenter)
        self.h_input.setValidator(QDoubleValidator(0, 239, 0))
        self.h_input.setText(str(self.h_c))
        self.h_input.textEdited.connect(
            lambda: self._update_hsl_input(self.h_input, "h")
        )
        grid.addWidget(self.h_input, 5, 1)

        s_label = QLabel("S")
        s_label.setFont(QFont("Arial", 12))
        s_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(s_label, 6, 0)

        self.s_input = QLineEdit()
        self.s_input.setFont(QFont("Arial", 12))
        self.s_input.setAlignment(Qt.AlignCenter)
        self.s_input.setValidator(QDoubleValidator(0, 240, 0))
        self.s_input.setText(str(self.s_c))
        self.s_input.textEdited.connect(
            lambda: self._update_hsl_input(self.s_input, "s")
        )
        grid.addWidget(self.s_input, 6, 1)

        l_label = QLabel("L")
        l_label.setFont(QFont("Arial", 12))
        l_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(l_label, 7, 0)

        self.l_input = QLineEdit()
        self.l_input.setFont(QFont("Arial", 12))
        self.l_input.setAlignment(Qt.AlignCenter)
        self.l_input.setValidator(QDoubleValidator(0, 240, 0))
        self.l_input.setText(str(self.l_c))
        self.l_input.textEdited.connect(
            lambda: self._update_hsl_input(self.l_input, "l")
        )
        grid.addWidget(self.l_input, 7, 1)

        # Color Preview
        self.color_preview = QLabel()
        self.color_preview.setStyleSheet(
            "background-color: rgb({}, {}, {});".format(
                int(self.r_c), int(self.g_c), int(self.b_c)
            )
        )
        self.color_preview.setFixedSize(100, 360)
        grid.addWidget(self.color_preview, 0, 2, 9, 2)

        grid.setRowStretch(10, 1)
        grid.setColumnStretch(2, 1)
        display_grid_on_window(window, grid)

    def rgb_to_hsl(self):
        self._convert_rgb_to_hsl(self.r_c, self.g_c, self.b_c)
        self.h_input.setText(str(int(self.h_c)))
        self.s_input.setText(str(int(self.s_c)))
        self.l_input.setText(str(int(self.l_c)))
        self.color_preview.setStyleSheet(
            "background-color: rgb({}, {}, {});".format(
                int(self.r_c), int(self.g_c), int(self.b_c)
            )
        )

    def hsl_to_rgb(self):
        self._convert_hsl_to_rgb(self.h_c, self.s_c, self.l_c)
        self.r_input.setText(str(int(self.r_c)))
        self.g_input.setText(str(int(self.g_c)))
        self.b_input.setText(str(int(self.b_c)))
        self.color_preview.setStyleSheet(
            "background-color: rgb({}, {}, {});".format(
                int(self.r_c), int(self.g_c), int(self.b_c)
            )
        )
