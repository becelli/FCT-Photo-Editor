from PyQt5.QtGui import QImage
import numpy as np
from modules.functions import (
    get_color_integer_from_color_name,
    get_color_integer_from_gray,
    get_color_integer_from_rgb,
    get_gray_from_color_integer,
    get_rgb_from_color_integer,
)
import libkayn as kayn


class Filters:
    def __init__(self, img: QImage):
        self.img: QImage = img

    def _create_new_image(self, width=320, height=240):
        image = QImage(width, height, QImage.Format.Format_RGB32)
        return image

    def _get_default_elements_to_filters(self) -> tuple:
        w, h = self.img.width(), self.img.height()
        image = self._create_new_image(w, h)
        return w, h, image

    def grayscale(self) -> QImage:
        w, h, new_image = self._get_default_elements_to_filters()
        image = np.array(self.img.bits().asarray(w * h * 4)).reshape(h * w, 4)[:, :3]
        grayscaled = kayn.grayscale(image)
        for y in range(h):
            for x in range(w):
                new_image.setPixel(x, y, grayscaled[x + y * w])
        return new_image

    def get_channel(self, color: str) -> QImage:
        w, h, image = self._get_default_elements_to_filters()
        for x in range(w):
            for y in range(h):
                pixel = self.img.pixel(x, y)
                new_pixel = get_color_integer_from_color_name(color, pixel)
                image.setPixel(x, y, new_pixel)
        return image

    def negative(self) -> QImage:
        w, h, new_image = self._get_default_elements_to_filters()
        image = np.array(self.img.bits().asarray(w * h * 4)).reshape(h * w, 4)[:, :3]
        negatived = kayn.negative(image)
        for y in range(h):
            for x in range(w):
                new_image.setPixel(x, y, negatived[x + y * w])
        return new_image

    def binarize(self) -> QImage:
        return self.limiarization(127)

    def salt_and_pepper(self, amount: float = 1) -> QImage:
        """
        Adds salt and pepper noise to an img.
        """
        from random import randint

        w, h = self.img.width(), self.img.height()
        image = self.img.copy()
        perc = int(amount * w * h // 100)

        for _ in range(perc // 2):
            x1, y1 = randint(0, w - 1), randint(0, h - 1)
            x2, y2 = randint(0, w - 1), randint(0, h - 1)
            image.setPixel(x2, y2, 0x00000000)
            image.setPixel(x1, y1, 0xFFFFFFFF)
        return image

    def equalize(self) -> QImage:
        w, h, image = self._get_default_elements_to_filters()
        n = w * h
        if self.img.isGrayscale():
            frequency = np.zeros(256)
            for x in range(w):
                for y in range(h):
                    pixel = self.img.pixel(x, y)
                    frequency[get_gray_from_color_integer(pixel)] += 1
            frequency = 255 * frequency / n  # 255 * freq / (w * h)
            cum_freq = np.cumsum(frequency)

            for x in range(w):
                for y in range(h):
                    pixel = self.img.pixel(x, y)
                    gray = get_gray_from_color_integer(pixel)
                    new_pixel = get_color_integer_from_gray(int(cum_freq[gray] - 1))
                    image.setPixel(x, y, new_pixel)
        else:
            r_freq, g_freq, b_freq = np.zeros(256), np.zeros(256), np.zeros(256)
            for x in range(w):
                for y in range(h):
                    pixel = self.img.pixel(x, y)
                    rgb = get_rgb_from_color_integer(pixel)
                    r_freq[rgb[0]] += 1
                    g_freq[rgb[1]] += 1
                    b_freq[rgb[2]] += 1
            r_freq = 255 * r_freq / n  # 255 * freq / (w * h)
            g_freq = 255 * g_freq / n  # 255 * freq / (w * h)
            b_freq = 255 * b_freq / n  # 255 * freq / (w * h)
            cum_r_freq = np.cumsum(r_freq)
            cum_g_freq = np.cumsum(g_freq)
            cum_b_freq = np.cumsum(b_freq)
            for x in range(w):
                for y in range(h):
                    pixel = self.img.pixel(x, y)
                    rgb = get_rgb_from_color_integer(pixel)
                    r = int(cum_r_freq[rgb[0]] - 1)
                    g = int(cum_g_freq[rgb[1]] - 1)
                    b = int(cum_b_freq[rgb[2]] - 1)
                    new_pixel = get_color_integer_from_rgb(r, g, b)
                    image.setPixel(x, y, new_pixel)
        return image

    def mean(self, n: int = 3) -> QImage:
        mask = np.ones(n * n) / (n * n)
        image = self.filter_NxN(mask)
        return image

    def median(self, n: int = 3) -> QImage:
        n = n if n % 2 == 1 else n + 1
        distance = int(n / 2)
        w, h = self.img.width(), self.img.height()

        new_w, new_h = w - n + 1, h - n + 1
        new_image = QImage(new_w, new_h, QImage.Format.Format_RGB32)

        image = np.array(self.img.bits().asarray(w * h * 4)).reshape(h * w, 4)[:, :3]
        median_img = kayn.median(image, distance, w, h)

        for y in range(new_h):
            for x in range(new_w):
                new_image.setPixel(x, y, median_img[x + y * new_w])

        return new_image

    def dynamic_compression(self, c: float = 1, gama: float = 1) -> QImage:
        w, h, image = self._get_default_elements_to_filters()
        f = (
            self._dynamic_compression_gray_pixel
            if self.img.isGrayscale()
            else self._dynamic_compression_colored_pixel
        )

        for x in range(w):
            for y in range(h):
                new_pixel = f(x, y, c, gama)
                image.setPixel(x, y, new_pixel)

        self.img = image
        normalized_img = self.normalize()
        return normalized_img

    def _dynamic_compression_gray_pixel(
        self, x: int, y: int, c: float = 1, gama: float = 1
    ) -> QImage:
        pixel = self.img.pixel(x, y)
        gray = get_gray_from_color_integer(pixel)
        new_color = min(255, int(c * (gray**gama)))
        new_pixel = get_color_integer_from_gray(new_color)
        return new_pixel

    def normalize(self, pixels=None) -> QImage:
        w, h = self.img.width(), self.img.height()
        image_to_use = lambda x, y: self.img.pixel(x, y)

        if pixels is not None:
            image_to_use = lambda x, y: pixels[x * h + y]
            w, h = pixels.shape[0], pixels.shape[1]
            pixels = pixels.reshape(w * h).astype(int)

        min_, max_, mode = None, None, None
        f = lambda fn, img: ([fn(int(img(x, y))) for x in range(w) for y in range(h)])
        if self.img.isGrayscale():
            pixels = f(get_gray_from_color_integer, image_to_use)
            min_, max_ = min(pixels), max(pixels)
            mode = self._get_normalized_gray_pixel
        else:
            pixels = f(get_rgb_from_color_integer, image_to_use)
            min_, max_ = np.min(pixels, axis=0), np.max(pixels, axis=0)
            mode = self._get_normalized_colored_pixel

        image = QImage(w, h, QImage.Format_RGB32)
        for x in range(w):
            for y in range(h):
                pixel = pixels[x * h + y]
                new_pixel = mode(pixel, min_, max_)
                image.setPixel(x, y, new_pixel)

        return image

    def _get_normalized_gray_pixel(self, pixel, min_, max_):
        norm = int(255 * (pixel - min_) / (max_ - min_))
        pixel_color = get_color_integer_from_gray(norm)
        return pixel_color

    def _get_normalized_colored_pixel(self, pixel, min_, max_):
        # fmt: off
        norm = tuple(int(255 * (pixel[i] - min_[i]) / (max_[i] - min_[i])) for i in range(3))
        pixel_color = get_color_integer_from_rgb(*norm)
        return pixel_color
        # fmt: on

    def _dynamic_compression_colored_pixel(
        self, x: int, y: int, c: float = 1, gama: float = 1
    ) -> QImage:
        pixel = self.img.pixel(x, y)
        rgb = get_rgb_from_color_integer(pixel)
        f = lambda i: min(255, int(c * (rgb[i] ** gama)))
        r, g, b = f(0), f(1), f(2)
        new_pixel = get_color_integer_from_rgb(r, g, b)
        return new_pixel

    def sobel(self) -> QImage:
        kernelX = np.array([-1, 0, 1, -2, 0, 2, -1, 0, 1]) / np.float64(4)
        kernelY = np.array([-1, -2, -1, 0, 0, 0, 1, 2, 1]) / np.float64(4)

        if not self.img.isGrayscale():
            self.img = self.grayscale()

        vertical = self.filter_NxN(kernelY)
        horizontal = self.filter_NxN(kernelX)
        w, h = vertical.width(), vertical.height()
        image = QImage(w, h, QImage.Format_RGB32)

        for x in range(w):
            for y in range(h):
                new_pixel = self._sobel_pixel(x, y, vertical, horizontal)
                image.setPixel(x, y, new_pixel)

        self.img = image
        normalized_img = self.normalize()
        return normalized_img

    def sobel_magnitudes(self) -> tuple[QImage, QImage, QImage]:
        kernelY = np.array([-1, -2, -1, 0, 0, 0, 1, 2, 1]) / np.float64(4)
        kernelX = np.array([-1, 0, 1, -2, 0, 2, -1, 0, 1]) / np.float64(4)

        if not self.img.isGrayscale():
            self.img = self.grayscale()

        vertical = self.filter_NxN(kernelY)
        horizontal = self.filter_NxN(kernelX)
        w, h = vertical.width(), vertical.height()
        image = QImage(w, h, QImage.Format_RGB32)

        for x in range(w):
            for y in range(h):
                new_pixel = self._sobel_pixel(x, y, vertical, horizontal)
                image.setPixel(x, y, new_pixel)

        return image, vertical, horizontal

    def _sobel_pixel(self, x: int, y: int, vertical: QImage, horizontal: QImage):
        vertical = vertical.pixel(x, y)
        horizontal = horizontal.pixel(x, y)
        cur_vertical = get_gray_from_color_integer(vertical)
        cur_horizontal = get_gray_from_color_integer(horizontal)
        c = int(np.abs(np.sqrt(cur_vertical**2 + cur_horizontal**2)))
        return get_color_integer_from_gray(c)

    def laplace(self) -> QImage:
        # mask = np.array([-1, -1, -1, -1, 9, -1,-1, -1, -1]) / np.float64(8)
        mask = np.array([0, -1, 0, -1, 4, -1, 0, -1, 0]) / np.float64(4)

        self.img = self.filter_NxN(mask)
        normalized_img = self.normalize()
        return normalized_img

    def resize_nearest_neighbor(self, w: int, h: int) -> QImage:
        image = self._create_new_image(w, h)
        ratio_x = self.img.width() / w
        ratio_y = self.img.height() / h
        for x in range(w):
            for y in range(h):
                new_pixel = self._resize_nearest_neighbor_pixel(x, y, ratio_x, ratio_y)
                image.setPixel(x, y, new_pixel)
        return image

    def _resize_nearest_neighbor_pixel(
        self, x: int, y: int, ratio_x: float, ratio_y: float
    ) -> QImage:
        x_ = int(x * ratio_x)
        y_ = int(y * ratio_y)
        return self.img.pixel(x_, y_)

    def limiarization(self, t: int = 160) -> QImage:
       #'Binarizes' an img at certain threshold.
        w, h, image = self._get_default_elements_to_filters()
        f = (
            self._limiarization_gray_pixel
            if self.img.isGrayscale()
            else self._limiarization_colored_pixel
        )

        for x in range(w):
            for y in range(h):
                new_pixel = f(x, y, t)
                image.setPixel(x, y, new_pixel)
        return image

    def _limiarization_gray_pixel(self, x, y, t):
        pixel = self.img.pixel(x, y)
        gray = get_gray_from_color_integer(pixel)
        if gray > t:
            return 0xFFFFFF
        else:
            return 0x000000

    def _limiarization_colored_pixel(self, x, y, t):
        pixel = self.img.pixel(x, y)
        r, g, b = get_rgb_from_color_integer(pixel)
        r, g, b = 255 if r > t else 0, 255 if g > t else 0, 255 if b > t else 0
        return get_color_integer_from_rgb(r, g, b)

    def filter_NxN(self, mask: np.ndarray) -> QImage:
        w, h = self.img.width(), self.img.height()
        f_size = mask.shape[0]
        side = int(f_size**0.5)

        image = np.array(self.img.bits().asarray(w * h * 4)).reshape(h * w, 4)[:, :3]
        filtered = kayn.filter_nxn(image, mask, w, h)

        new_w, new_h = w - side + 1, h - side + 1
        new_image = QImage(new_w, new_h, QImage.Format.Format_RGB32)
        for x in range(new_w):
            for y in range(new_h):
                new_image.setPixel(x, y, filtered[x * new_h + y])

        return new_image

        """
        
        def discrete_cousine_transform(self) -> QImage:
        
                w, h, image = self._get_default_elements_to_filters()
                ci, cj, dctl, sum_ = 0.0, 0.0, 0.0, 0.0
        
                entry = np.ones((8, 8)) * np.int64(255)
                result = np.zeros((8, 8))
                w, h = 8, 8
        
                alpha = lambda u, n: np.sqrt(1 / n) if u == 0 else np.sqrt(2.0 / n)
                for u in range(w):
                    for v in range(h):
                        ci = alpha(u, w)
                        cj = alpha(v, h)
                        sum_ = np.float(0)
                        for x in range(w):
                            for y in range(h):
                                pixel = entry[x][y]
        
                                dctl = pixel
                                dctl *= np.cos((2 * x + 1) * u * np.pi / (2.0 * w))
                                dctl *= np.cos((2 * y + 1) * v * np.pi / (2.0 * h))
                                sum_ += dctl
        
                        result[u][v] = sum_ * ci * cj
        
        """
