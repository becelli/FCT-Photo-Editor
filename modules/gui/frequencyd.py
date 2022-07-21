from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QPushButton
import modules.gui.qt_override as qto
from modules.filters import Filters
from PyQt5.QtWidgets import QMessageBox


class FreqDomain:
    def __init__(self, parent, input_canvas, output_canvas):
        self.parent = parent
        self.window = qto.QChildWindow(self.parent, "Frequency Domain", 400, 400)
        self.input_canvas = input_canvas
        self.output_canvas = output_canvas
        self.show_freq_domain_window()

    def show_freq_domain_window(self):
        img = qto.get_image_from_canvas(self.input_canvas)
        self.w, self.h = img.width(), img.height()
        if self.w != self.h:
            QMessageBox.warning(
                self.parent, "Frequency Domain", "Image must be square."
            )
            return

        self.add_submenus()
        self.grid = qto.QGrid(self.window)

        f_label, self.f_canvas = qto.create_label_and_canvas("Frequency Domain")
        s_label, self.s_canvas = qto.create_label_and_canvas("Space Domain")
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(lambda: self.apply_changes())

        self.grid.addWidget(f_label, 0, 0)
        self.grid.addWidget(self.f_canvas, 1, 0)
        self.grid.addWidget(s_label, 0, 1)
        self.grid.addWidget(self.s_canvas, 1, 1)
        self.grid.addWidget(apply_btn, 2, 0, 1, 2)
        self.grid.setRowStretch(1, 1)
        self.grid.setColumnStretch(1, 1)
        qto.display_grid_on_window(self.window, self.grid)

        norm, self.freq = Filters.DCT(img)
        qto.put_image_on_canvas(self.f_canvas, norm)
        qto.put_image_on_canvas(self.s_canvas, img)

    def open_image(self):
        print("Open image")
        file_name = qto.QDialogs(self.parent).get_open_path()
        if not file_name:
            return
        img = QPixmap(file_name).toImage()
        self.w, self.h = img.width(), img.height()
        if self.w != self.h:
            QMessageBox.warning(
                self.parent, "Frequency Domain", "Image must be square."
            )
            return
        qto.put_image_on_canvas(self.input_canvas, img)
        norm, self.freq = Filters.DCT(img)
        qto.put_image_on_canvas(self.f_canvas, norm)
        qto.put_image_on_canvas(self.s_canvas, img)

    def lowpass(self):
        radius = qto.display_int_input_dialog("Radius", 0, self.w, self.w // 2)
        if radius > 0:
            norm, self.freq = Filters.lowpass(self.freq, self.w, self.h, radius)
            qto.put_image_on_canvas(self.f_canvas, norm)
            output = Filters.IDCT(self.freq, self.w, self.h)
            qto.put_image_on_canvas(self.s_canvas, output)

    def highpass(self):
        radius = qto.display_int_input_dialog("Radius", 0, self.w, self.w // 2)
        norm, self.freq = Filters.highpass(self.freq, self.w, self.h, radius)
        qto.put_image_on_canvas(self.f_canvas, norm)
        output = Filters.IDCT(self.freq, self.w, self.h)
        qto.put_image_on_canvas(self.s_canvas, output)

    def add_noise(self):
        self.f_canvas.mousePressEvent = self.add_noise_to_freq_canvas
        self.add_noise_btn.setEnabled(False)
        self.stop_noise_btn.setEnabled(True)

    def stop_noise(self):
        def do_nothing(e):
            pass

        self.f_canvas.mousePressEvent = do_nothing
        self.add_noise_btn.setEnabled(True)
        self.stop_noise_btn.setEnabled(False)

    def add_noise_to_freq_canvas(self, event):
        x, y = event.x(), event.y()
        if x < 0 or y < 0 or x >= self.w or y >= self.h:
            return
        max_ = max(self.freq)
        self.freq[x + y * self.w] = max_ / 4

        output = Filters.IDCT(self.freq, self.w, self.h)
        qto.put_image_on_canvas(self.s_canvas, output)

        norm = Filters.get_freq_norm(self.freq, self.w, self.h)
        qto.put_image_on_canvas(self.f_canvas, norm)

    def add_submenus(self):
        menubar = self.window.menuBar()
        menubar.addAction("Open", self.open_image)
        menubar.addAction("Exit", self.window.close)

        self.filter_menu = menubar.addMenu("Filter")
        self.filter_menu.addAction("Lowpass", self.lowpass)
        self.filter_menu.addAction("Highpass", self.highpass)

        self.add_noise_btn = menubar.addAction("Add Noise", self.add_noise)
        self.stop_noise_btn = menubar.addAction("Stop Noise", self.stop_noise)
        self.stop_noise_btn.setEnabled(False)

    def apply_changes(self):
        self.output_canvas.setPixmap(self.s_canvas.pixmap())
        self.window.close()
