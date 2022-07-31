import modules.gui.qt_override as qto
from modules.filters import Filters


class Comparison:
    def __init__(self, parent, input_canvas):
        self.parent = parent
        self.window = qto.QChildWindow(
            self.parent, "Laplacian vs Laplacian of Gaussian", 660, 400
        )
        self.input_canvas = input_canvas
        self.show_window()

    def show_window(self):
        img = qto.get_image_from_canvas(self.input_canvas)
        w, h = img.width(), img.height()
        ratio = w / 320
        w, h = int(w / ratio), int(h / ratio)

        self.grid = qto.QGrid(self.window)

        l_label, self.l_canvas = qto.create_label_and_canvas("Laplacian", w, h)
        log_label, self.log_canvas = qto.create_label_and_canvas(
            "Laplacian of Gaussian", w, h
        )

        f = Filters(img)
        laplacian = f.laplace()
        log = f.gaussian_laplacian()
        qto.put_image_on_canvas(self.l_canvas, laplacian)
        qto.put_image_on_canvas(self.log_canvas, log)

        self.grid.addWidget(l_label, 0, 0)
        self.grid.addWidget(self.l_canvas, 1, 0)
        self.grid.addWidget(log_label, 0, 1)
        self.grid.addWidget(self.log_canvas, 1, 1)
        self.grid.setRowStretch(1, 1)
        self.grid.setColumnStretch(1, 1)
        qto.display_grid_on_window(self.window, self.grid)
