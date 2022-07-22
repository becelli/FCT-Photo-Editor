from dataclasses import dataclass
from PyQt5.QtGui import QImage
import numpy as np
import modules.colors_adapter as c_adpt
import libkayn as kayn


@dataclass
class Filters:
    img: QImage

    def _default_filter(self, filter_func: callable, **kwargs) -> QImage:
        w, h = self.img.width(), self.img.height()
        image = self._get_img_pixels(w, h)

        filtered = filter_func(image, **kwargs)

        new_image = QImage(w, h, QImage.Format.Format_RGB32)
        for y in range(h):
            for x in range(w):
                new_image.setPixel(x, y, filtered[x + y * w])
        return new_image

    def _create_new_image(self, width=320, height=240):
        image = QImage(width, height, QImage.Format.Format_RGB32)
        return image

    def _get_default_elements_to_filters(self) -> tuple:
        w, h = self.img.width(), self.img.height()
        image = self._create_new_image(w, h)
        return w, h, image

    def _get_img_pixels(self, w, h):
        bits = np.array(self.img.bits().asarray(w * h * 4))
        # Reverse the order of the pixels to match the order of the image
        pixels = bits.reshape(h * w, 4)[:, :3][:, ::-1]
        return pixels

    def grayscale(self) -> QImage:
        if self.img.isGrayscale():
            return self.img
        return self._default_filter(kayn.grayscale)

    def split_color_channel(self, channel: str) -> QImage:
        ch = 0 if channel == "red" else 1 if channel == "green" else 2
        return self._default_filter(kayn.split_color_channel, channel=ch)

    def negative(self) -> QImage:
        return self._default_filter(kayn.negative)

    def binarize(self, limiar: int) -> QImage:
        w, h = self.img.width(), self.img.height()
        image = self._get_img_pixels(w, h)
        binarized = kayn.binarize(image, limiar)
        new_image = QImage(w, h, QImage.Format.Format_RGB32)
        for y in range(h):
            for x in range(w):
                new_image.setPixel(x, y, binarized[x + y * w])
        return new_image

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
        w, h = self.img.width(), self.img.height()
        image = self._get_img_pixels(w, h)
        equalized = kayn.equalize(image)
        new_image = QImage(w, h, QImage.Format.Format_RGB32)
        for y in range(h):
            for x in range(w):
                new_image.setPixel(x, y, equalized[x + y * w])
        return new_image

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

        image = self._get_img_pixels(w, h)
        median_img = kayn.median(image, distance, w, h)

        for y in range(new_h):
            for x in range(new_w):
                new_image.setPixel(x, y, median_img[x + y * new_w])

        return new_image

    def dynamic_compression(self, c: float = 1, gamma: float = 1) -> QImage:
        return self._default_filter(kayn.dynamic_compression, constant=c, gamma=gamma)

    def normalize(self) -> QImage:
        return self._default_filter(kayn.normalize)

    def sobel(self) -> QImage:
        kernelX = np.array([-1, 0, 1, -2, 0, 2, -1, 0, 1]) / np.float64(4)
        kernelY = np.array([-1, -2, -1, 0, 0, 0, 1, 2, 1]) / np.float64(4)

        if not self.img.isGrayscale():
            self.img = self.grayscale()

        vertical = self.filter_NxN(kernelY)
        horizontal = self.filter_NxN(kernelX)
        w, h = vertical.width(), vertical.height()
        image = QImage(w, h, QImage.Format.Format_RGB32)

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
        vert = vertical.pixel(x, y)
        horiz = horizontal.pixel(x, y)
        cur_vertical = c_adpt.get_gray_from_color_integer(vert)
        cur_horizontal = c_adpt.get_gray_from_color_integer(horiz)
        c = int(np.abs(np.sqrt(cur_vertical**2 + cur_horizontal**2)))
        return c_adpt.get_color_integer_from_gray(c)

    def laplace(self) -> QImage:
        mask = np.array([0, -1, 0, -1, 4, -1, 0, -1, 0]) / np.float64(4)

        self.img = self.filter_NxN(mask)
        normalized_img = self.normalize()
        return normalized_img

    # fmt: off
    def gaussian_laplacian(self) -> QImage:
        mask = np.array(
            [
                 0,  0, -1,  0,  0,
                 0, -1, -2, -1,  0,
                -1, -2, 16, -2, -1,
                 0, -1, -2, -1,  0,
                 0,  0, -1,  0,  0,
            ]
        ) / np.float64(16)
        self.img = self.filter_NxN(mask)
        normalized_img = self.normalize()
        return normalized_img

    def resize_nearest_neighbor(self, new_width: int, new_height: int) -> QImage:
        w, h = self.img.width(), self.img.height()
        image = self._get_img_pixels(w, h)
        new_image = QImage(new_width, new_height, QImage.Format.Format_RGB32)
        resized = kayn.resize_nn(image, w, h, new_width, new_height)
        for y in range(new_height):
            for x in range(new_width):
                new_image.setPixel(x, y, resized[x + y * new_width])
        return new_image

    def limiarize(self, threshold: int) -> QImage:
        return self._default_filter(kayn.limiarize, threshold=threshold)

    def filter_NxN(self, mask: np.ndarray) -> QImage:
        w, h = self.img.width(), self.img.height()
        f_size = mask.shape[0]
        side = int(f_size**0.5)

        image = self._get_img_pixels(w, h)
        filtered = kayn.filter_nxn(image, mask, w, h)

        new_w, new_h = w - side + 1, h - side + 1
        new_image = QImage(new_w, new_h, QImage.Format.Format_RGB32)
        for x in range(new_w):
            for y in range(new_h):
                new_image.setPixel(x, y, filtered[x * new_h + y])

        return new_image

    def gray_to_color_scale(self) -> QImage:
        return self._default_filter(kayn.gray_to_color_scale)

    def noise_reduction_max(self, n: int = 3) -> QImage:
        n = n if n % 2 == 1 else n + 1
        distance = int(n / 2)
        w, h = self.img.width(), self.img.height()

        new_w, new_h = w - n + 1, h - n + 1
        new_image = QImage(new_w, new_h, QImage.Format.Format_RGB32)

        image = self._get_img_pixels(w, h)
        maxed_img = kayn.noise_reduction_max(image, distance, w, h)

        for y in range(new_h):
            for x in range(new_w):
                new_image.setPixel(x, y, maxed_img[x + y * new_w])

        return new_image

    def noise_reduction_min(self, n: int = 3) -> QImage:
        n = n if n % 2 == 1 else n + 1
        distance = int(n / 2)
        w, h = self.img.width(), self.img.height()

        new_w, new_h = w - n + 1, h - n + 1
        new_image = QImage(new_w, new_h, QImage.Format.Format_RGB32)

        image = self._get_img_pixels(w, h)
        minimal_img = kayn.noise_reduction_min(image, distance, w, h)

        for y in range(new_h):
            for x in range(new_w):
                new_image.setPixel(x, y, minimal_img[x + y * new_w])

        return new_image

    def noise_reduction_midpoint(self, n: int = 3) -> QImage:
        n = n if n % 2 == 1 else n + 1
        distance = int(n / 2)
        w, h = self.img.width(), self.img.height()

        new_w, new_h = w - n + 1, h - n + 1
        new_image = QImage(new_w, new_h, QImage.Format.Format_RGB32)

        image = self._get_img_pixels(w, h)
        median_img = kayn.noise_reduction_midpoint(image, distance, w, h)

        for y in range(new_h):
            for x in range(new_w):
                new_image.setPixel(x, y, median_img[x + y * new_w])

        return new_image

    @staticmethod
    def DCT(image) -> tuple[QImage, np.ndarray]:        
        f = Filters(image)
        if not image.isGrayscale():
            f.img = f.grayscale()
        
        w, h, new_image = f._get_default_elements_to_filters()
        image = f._get_img_pixels(w, h)
        norm, coeffs = kayn.dct(image, w, h)

        for y in range(h):
            for x in range(w):
                new_image.setPixel(x, y, norm[x + y * w])
        return new_image, coeffs

    @staticmethod
    def IDCT(coeffs, width, height) -> QImage:
        image = QImage(width, height, QImage.Format.Format_RGB32)
        norm = kayn.idct(coeffs, width, height)
        for x in range(width):
            for y in range(height):
                image.setPixel(x, y, norm[x + y * width])
        return image
    
    @staticmethod
    def lowpass(coeffs, width, height, radius) -> tuple[QImage, np.ndarray]:
        norm, new_coeffs = kayn.freq_lowpass(coeffs, width, height, radius)
        new_image = Filters.IDCT(new_coeffs, width, height)
        for x in range(width):
            for y in range(height):
                new_image.setPixel(x, y, norm[x + y *  width])
        return new_image, new_coeffs
    
    @staticmethod
    def highpass(coeffs, width, height, radius) -> tuple[QImage, np.ndarray]:
        norm, new_coeffs = kayn.freq_highpass(coeffs, width, height, radius)
        new_image = Filters.IDCT(new_coeffs, width, height)
        for x in range(width):
            for y in range(height):
                new_image.setPixel(x, y, norm[x + y *  width])
        return new_image, new_coeffs
    
    @staticmethod
    def get_freq_norm(coeffs, width, height) -> QImage:
        norm = kayn.freq_normalize(coeffs)
        new_image = QImage(width, height, QImage.Format.Format_RGB32)
        for x in range(width):
            for y in range(height):
                new_image.setPixel(x, y, norm[x + y *  width])
        return new_image


    def otsu_binarize(self) -> QImage:
        w, h = self.img.width(), self.img.height()
        image = self._get_img_pixels(w, h)
        threshold = kayn.otsu_threshold(image, w, h)
        return self._default_filter(kayn.binarize, threshold=threshold)

    def otsu_limiarize(self) -> QImage:
        w, h = self.img.width(), self.img.height()
        image = self._get_img_pixels(w, h)
        threshold = kayn.otsu_threshold(image, w, h)
        return self._default_filter(kayn.limiarize, threshold=threshold)

    def hsl_equalize(self) -> QImage:
        w, h = self.img.width(), self.img.height()
        return self._default_filter(kayn.equalize_hsl, w, h)
