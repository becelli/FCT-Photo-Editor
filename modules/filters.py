# Import QImage and QPixmap
from PyQt5.QtGui import QImage, QPixmap, QColor, qRgb, qRed, qGreen, qBlue
from ctypes import *
import numpy as np
import time
from modules.functions import gray_from_rgb

# import buffer


class Filters:
    def __init__(self, img: QImage):
        self.img: QImage = img

    def grayscale(self) -> QImage:
        """
        Converts an img to a grayscale version.
        """

        if self.img.isGrayscale():
            return None

        w, h = self.img.width(), self.img.height()
        image = QImage(w, h, QImage.Format_RGB888)
        for x in range(w):
            for y in range(h):
                c = QColor(self.img.pixel(x, y)).getRgb()[:3]
                color = gray_from_rgb(*c)
                image.setPixel(x, y, qRgb(color, color, color))
        return image

    def get_channel(self, color: str) -> QImage:
        """
        Separates the channels of an img.
        """

        w, h = self.img.width(), self.img.height()
        image = QImage(w, h, QImage.Format_RGB888)
        f = None
        match color:
            case "red":
                f = lambda pixel: qRgb(qRed(pixel), 0, 0)
            case "green":
                f = lambda pixel: qRgb(0, qGreen(pixel), 0)
            case "blue":
                f = lambda pixel: qRgb(0, 0, qBlue(pixel))

        for x in range(w):
            for y in range(h):
                image.setPixel(x, y, f(self.img.pixel(x, y)))
        return image

    def negative(self) -> QImage:
        """
        Inverts the colors of an img.
        """
        w, h = self.img.width(), self.img.height()
        image = QImage(w, h, QImage.Format_RGB888)
        if self.img.isGrayscale():
            for x in range(w):
                for y in range(h):
                    color = 255 - qRed(self.img.pixel(x, y))
                    image.setPixel(x, y, qRgb(color, color, color))
        else:
            for x in range(w):
                for y in range(h):
                    pix = self.img.pixel(x, y)
                    p = [qRed(pix), qGreen(pix), qBlue(pix)]
                    image.setPixel(x, y, qRgb(255 - p[0], 255 - p[1], 255 - p[2]))
        return image

    def binarize(self, threshold: int = 127) -> QImage:
        """
        Binarizes the intensity of the pixels.
        For Grayscale QImages, it's known as a real B&W.
        For RGB Qimages, it will binarize each color channel.
        """

        # Grayscale
        w, h = self.img.width(), self.img.height()
        image = QImage(w, h, QImage.Format_RGB888)
        f = None
        if self.img.isGrayscale():
            f = (
                lambda pixel: qRgb(255, 255, 255)
                if pixel[0] > threshold
                else qRgb(0, 0, 0)
            )
        else:
            f = lambda pixel: qRgb(
                255 if pixel[0] > threshold else 0,
                255 if pixel[1] > threshold else 0,
                255 if pixel[2] > threshold else 0,
            )

        for x in range(w):
            for y in range(h):
                pixel = QColor(self.img.pixel(x, y)).getRgb()
                image.setPixel(x, y, f(pixel))
        return image

    def salt_and_pepper(self, amount: float = 1) -> QImage:
        """
        Adds salt and pepper noise to an img.
        """
        from random import randint

        w, h = self.img.width(), self.img.height()
        image = self.img.copy()
        perc = int((amount / 100) * w * h)

        for _ in range(perc // 2):
            x1, y1 = randint(0, w - 1), randint(0, h - 1)
            x2, y2 = randint(0, w - 1), randint(0, h - 1)
            image.setPixel(x1, y1, qRgb(0, 0, 0))
            image.setPixel(x2, y2, qRgb(255, 255, 255))
        return image

    def equalize(self) -> QImage:
        """
        Equalizes the intensity of an img.
        """
        w, h = self.img.width(), self.img.height()
        n = w * h
        image = QImage(w, h, QImage.Format_RGB888)
        # Get all self.img pixels
        if self.img.isGrayscale():
            frequency = np.zeros(256)
            for x in range(w):
                for y in range(h):
                    frequency[QColor(self.img.pixel(x, y)).getRgb()[0]] += 1
            # Cumulative distribution function
            frequency = 255 * frequency / n  # 255 * freq / (w * h)
            cum_freq = np.cumsum(frequency)

            # for i, p in enumerate(canvas):
            for x in range(w):
                for y in range(h):
                    p = QColor(self.img.pixel(x, y)).getRgb()
                    val = int(cum_freq[p[0]] - 1)
                    image.setPixel(x, y, qRgb(val, val, val))
        else:
            r_freq, g_freq, b_freq = np.zeros(256), np.zeros(256), np.zeros(256)
            for x in range(w):
                for y in range(h):
                    pixel = QColor(self.img.pixel(x, y)).getRgb()
                    r_freq[pixel[0]] += 1
                    g_freq[pixel[1]] += 1
                    b_freq[pixel[2]] += 1

            r_freq = 255 * r_freq / n  # 255 * freq / (w * h)
            g_freq = 255 * g_freq / n  # 255 * freq / (w * h)
            b_freq = 255 * b_freq / n  # 255 * freq / (w * h)
            cum_r_freq = np.cumsum(r_freq)
            cum_g_freq = np.cumsum(g_freq)
            cum_b_freq = np.cumsum(b_freq)

            for x in range(w):
                for y in range(h):
                    p = QColor(self.img.pixel(x, y)).getRgb()
                    r = int(cum_r_freq[p[0]] - 1)
                    g = int(cum_g_freq[p[1]] - 1)
                    b = int(cum_b_freq[p[2]] - 1)
                    image.setPixel(x, y, qRgb(r, g, b))

        return image

    def apply_mask(
        self,
        mask: np.ndarray,
    ) -> QImage:
        """
        Applies a mask to an img.
        """
        a, b = mask.shape
        pa, pb = a // 2, b // 2
        w, h = self.img.width() - a + 1, self.img.height() - b + 1
        image = QImage(w, h, QImage.Format_RGB888)
        if self.img.isGrayscale():
            for x in range(w):
                for y in range(h):
                    area = self.get_pixel_area(x + pa, y + pb, (a, b))
                    new = 0.0
                    for i in range(a):
                        for j in range(b):
                            new += area[i * 3 + j][0] * mask[i][j]
                    new = int(new)
                    image.setPixel(x, y, qRgb(new, new, new))
        else:
            for x in range(w):
                for y in range(h):
                    new = [0, 0, 0]
                    area = self.get_pixel_area(x + pb, y + pb, (a, b))
                    for i in range(a):
                        for j in range(b):
                            for k in range(3):
                                new[k] += area[i * 3 + j][k] * mask[i][j]
                    image.setPixel(x, y, qRgb(int(new[0]), int(new[1]), int(new[2])))
        return image

    def get_pixel_area(self, x, y, size) -> np.ndarray:
        """
        Returns the area of a pixel.
        """
        # Pixels to left/right and top/bottom.
        a, b = size[0] // 2, size[1] // 2
        # Area around the pixel.
        area = np.zeros((size[0] * size[1], 3))

        # Running around the (x, y) pixel.

        it = 0
        for i in range(x - a, x + a + 1):
            for j in range(y - b, y + b + 1):
                area[it] = QColor(self.img.pixel(i, j)).getRgb()[:3]
                it += 1
        # All n = (a * b) pixels around, including the (x, y) pixel.
        return area

    def blur(self, n=3) -> QImage:
        """
        Blurs an img.
        """
        mask = np.ones((n, n)) / np.float64(n * n)  # 1/9 mask
        pixmap = self.apply_mask(mask)
        return pixmap

    def blur_median(self) -> QImage:
        """
        Blurs an img.
        """
        mask = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]) / np.float64(5)

        pixmap = self.apply_mask(mask)
        return pixmap

    def dynamic_compression(self, c: float = 1, gama: float = 1) -> QImage:
        """
        Blurs an img.
        """
        image = QImage(self.img)
        w, h = image.width(), image.height()
        c = 1
        f = lambda p: int(c * (p**gama))
        for x in range(w):
            for y in range(h):
                p = QColor(image.pixel(x, y)).getRgb()
                r = min(255, max(0, f(p[0])))
                g = min(255, max(0, f(p[1])))
                b = min(255, max(0, f(p[2])))
                image.setPixel(x, y, qRgb(r, g, b))
        return image
