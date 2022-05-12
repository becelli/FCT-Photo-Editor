from PyQt5.QtGui import QImage, QColor
from classes.image import Image
import numpy as np


class Adapter:
    @staticmethod
    def QImg2Img(qimage: QImage) -> Image:
        w, h = qimage.width(), qimage.height()
        canvas = np.zeros((h * w, 3)).astype(np.uint8)
        for y in range(h):
            for x in range(w):
                canvas[y * w + x] = np.array(
                    QColor(qimage.pixel(x, y)).getRgb()[:3]
                ).astype(np.uint8)
        return Image(size=[w, h], canvas=canvas)

    @staticmethod
    def Img2QImg(image: Image) -> QImage:
        w, h = image.get_size()
        img = QImage(w, h, QImage.Format.Format_RGB32)
        canvas = image.get_canvas()
        for x in range(w):
            for y in range(h):
                c = canvas[y * w + x]
                img.setPixel(x, y, QColor(c[0], c[1], c[2]).rgb())
        return img
