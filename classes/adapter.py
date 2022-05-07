from PyQt6.QtGui import QImage, QColor
from classes.image import Image


class Adapter:
    @staticmethod
    def QImg2Img(qimage: QImage, isRGB: bool = False) -> Image:
        canvas = []
        for y in range(qimage.height()):
            for x in range(qimage.width()):
                pixel = qimage.pixel(x, y)
                color = QColor(pixel)
                canvas.append(color.getRgb())

        return Image(size=[qimage.width(), qimage.height()], canvas=canvas, isRGB=isRGB)

    @staticmethod
    def Img2QImg(image: Image) -> QImage:
        img = QImage(image.get_width(), image.get_height(), QImage.Format.Format_RGB32)
        for x in range(image.get_width()):
            for y in range(image.get_height()):
                color = image.get_pixel(x, y)
                img.setPixel(x, y, QColor(color[0], color[1], color[2]).rgb())

        return img
