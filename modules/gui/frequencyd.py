from dataclasses import dataclass
from PyQt5 import QtWidgets, QtCore, QtGui
import modules.gui.qt_override as qto

# Import qt library to show Warnings
from modules.filters import Filters
from PyQt5.QtWidgets import QMessageBox


class FreqDomain:
    def __init__(self, parent, input_canvas, output_canvas):
        self.parent = parent
        self.input_canvas = input_canvas
        self.output_canvas = output_canvas
        self.show_freq_domain_window()

    def show_freq_domain_window(self):
        window = qto.QChildWindow(self.parent, "Frequency Domain", 1280, 800)
        grid = qto.QGrid(window)

        f_label, self.f_canvas = qto.create_label_and_canvas("Frequency Domain")
        i_label, self.i_canvas = qto.create_label_and_canvas("Image Domain")

        grid.addWidget(f_label, 0, 0)
        grid.addWidget(self.f_canvas, 1, 0)
        grid.addWidget(i_label, 0, 1)
        grid.addWidget(self.i_canvas, 1, 1)

        qto.display_grid_on_window(window, grid)
        # Put the images on the canvases

        img = QtGui.QPixmap("resources/cosine.bmp").toImage()

        # img = qto.get_image_from_canvas(self.input_canvas)
        qto.put_image_on_canvas(self.i_canvas, img)

        norm, freq = Filters.DCT(img)
        w, h = norm.width(), norm.height()
        idct = Filters.IDCT(freq, w, h)
        qto.put_image_on_canvas(self.f_canvas, idct)
        grid.setRowStretch(1, 1)
        grid.setColumnStretch(1, 1)
