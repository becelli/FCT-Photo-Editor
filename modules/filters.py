from PyQt5.QtGui import QImage
import numpy as np
import modules.colors_adapter as c_adpt
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

    def _get_img_pixels(self, w, h):
        pixels = np.array(self.img.bits().asarray(w * h * 4)).reshape(h * w, 4)[:, :3]
        return pixels

    def grayscale(self) -> QImage:
        if self.img.isGrayscale():
            return self.img
        w, h, new_image = self._get_default_elements_to_filters()
        image = self._get_img_pixels(w, h)
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
                new_pixel = c_adpt.get_color_integer_from_color_name(color, pixel)
                image.setPixel(x, y, new_pixel)
        return image

    def negative(self) -> QImage:
        w, h, new_image = self._get_default_elements_to_filters()
        image = self._get_img_pixels(w, h)
        negative = kayn.negative(image)
        for y in range(h):
            for x in range(w):
                new_image.setPixel(x, y, negative[x + y * w])
        return new_image

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

    def dynamic_compression(self, c: float = 1, gama: float = 1) -> QImage:
        w, h, new_image = self._get_default_elements_to_filters()
        image = self._get_img_pixels(w, h)
        compressed = kayn.dynamic_compression(image, c, gama)

        for y in range(h):
            for x in range(w):
                new_image.setPixel(x, y, compressed[x + y * w])

        # normalized = kayn.normalize(new_image)
        return new_image

    def normalize(self, pixels=None) -> QImage:
        w, h = self.img.width(), self.img.height()
        image = self._get_img_pixels(w, h)
        normalized = kayn.normalize(image)
        new_image = QImage(w, h, QImage.Format.Format_RGB32)
        for y in range(h):
            for x in range(w):
                new_image.setPixel(x, y, normalized[x + y * w])
        return new_image

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
        mask = np.array([-1, -1, -1, -1, 8, -1, -1, -1, -1]) / np.float64(8)
        # mask = np.array([0, -1, 0, -1, 4, -1, 0, -1, 0]) / np.float64(4)

        self.img = self.filter_NxN(mask)
        normalized_img = self.normalize()
        return normalized_img

    def gaussian_laplacian(self) -> QImage:
        mask = np.array(
            [
                0,
                0,
                -1,
                0,
                0,
                0,
                -1,
                -2,
                -1,
                0,
                -1,
                -2,
                16,
                -2,
                -1,
                0,
                -1,
                -2,
                -1,
                0,
                0,
                0,
                -1,
                0,
                0,
            ]
        ) / np.float64(16)
        self.img = self.filter_NxN(mask)
        normalized_img = self.normalize()
        return normalized_img

    def nevatia_babu(self) -> QImage:
        mask = np.array(
            [
                100,
                100,
                0,
                100,
                100,
                100,
                100,
                0,
                100,
                100,
                100,
                100,
                0,
                100,
                100,
                100,
                100,
                0,
                100,
                100,
                100,
                100,
                0,
                100,
                100,
            ]
        ) / np.float64(1000)
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

    def limiarization(self, limiar: int) -> QImage:
        w, h = self.img.width(), self.img.height()
        image = self._get_img_pixels(w, h)
        limiarized = kayn.limiarize(image, limiar)
        new_image = QImage(w, h, QImage.Format.Format_RGB32)
        for y in range(h):
            for x in range(w):
                new_image.setPixel(x, y, limiarized[x + y * w])
        return new_image

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
        w, h = self.img.width(), self.img.height()
        image = self._get_img_pixels(w, h)
        if not self.img.isGrayscale():
            self.img = self.grayscale()
        new_image = QImage(w, h, QImage.Format.Format_RGB32)
        colorized = kayn.gray_to_color_scale(image)
        for y in range(h):
            for x in range(w):
                new_image.setPixel(x, y, colorized[x + y * w])
        return new_image

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

    def DCT(self) -> QImage:
        # Discrete Cosine Transform
        w, h, new_image = self._get_default_elements_to_filters()
        image = self._get_img_pixels(w, h)

        if not self.img.isGrayscale():
            self.img = self.grayscale()

        norm, transf = kayn.dct(image, w, h)
        testing = kayn.idct(transf, w, h)

        for y in range(h):
            for x in range(w):
                new_image.setPixel(x, y, testing[x + y * w])
        return new_image

    def otsu_thresholding(self) -> QImage:
        w, h = self.img.width(), self.img.height()
        image = self._get_img_pixels(w, h)
        
        if not self.img.isGrayscale():
            self.img = self.grayscale()
        
        limiar = kayn.otsu_thresholding(image, w, h)
        limiarized = kayn.limiarize(image, limiar)
        new_image = QImage(w, h, QImage.Format.Format_RGB32)
        for y in range(h):
            for x in range(w):
                new_image.setPixel(x, y, limiarized[x + y * w])
        return new_image
