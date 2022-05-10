from classes.image import Image
from ctypes import *
import numpy as np
from modules.functions import gray_from_rgb


class Filters:
    def __init__(self, img: Image):
        self.img: Image = img
        self.isRGB = self._verify_is_RGB()

    def _verify_is_RGB(self) -> bool:
        for pixel in self.img.get_canvas():
            if pixel[0] != pixel[1] or pixel[0] != pixel[2]:
                return True
        return False

    def grayscale(self) -> Image:
        """
        Converts an img to a grayscale version.
        """
        if not self.isRGB:  # Verify if the img is already grayscale
            return self.img

        # Average of the RGB values

        def new_pixel(p):
            c = gray_from_rgb(p[0], p[1], p[2])
            return [c, c, c]

        size = self.img.get_size()
        pixels = np.zeros((size[0] * size[1], 3)).astype(np.uint8)
        canvas = self.img.get_canvas()
        for i, pixel in enumerate(canvas):
            pixels[i] = new_pixel(pixel)

        return Image(size=self.img.get_size(), canvas=pixels)

    def channels_separation(self) -> list[Image, Image, Image]:
        """
        Separates the channels of an img.
        """
        size = self.img.get_size()
        n = size[0] * size[1]
        red = np.zeros((n, 3)).astype(np.uint8)
        green = np.zeros((n, 3)).astype(np.uint8)
        blue = np.zeros((n, 3)).astype(np.uint8)
        for i, pixel in enumerate(self.img.get_canvas()):
            red[i] = [pixel[0], 0, 0]
            green[i] = [0, pixel[1], 0]
            blue[i] = [0, 0, pixel[2]]
        return Image(size, red), Image(size, green), Image(size, blue)

    def negative(self) -> Image:
        """
        Inverts the colors of an img.
        """
        canvas = self.img.get_canvas()
        pixels = np.zeros((self.img.count_pixels(), 3)).astype(np.uint8)
        if not self.isRGB:
            for i, pixel in enumerate(canvas):
                neg = 255 - pixel[0]
                pixels[i] = np.array([neg, neg, neg]).astype(np.uint8)
        else:
            for i, pixel in enumerate(canvas):
                pixels[i] = np.array(
                    [255 - pixel[0], 255 - pixel[1], 255 - pixel[2]]
                ).astype(np.uint8)

        return Image(size=self.img.get_size(), canvas=pixels)

    def binarize(self, threshold: int = 128) -> Image:
        """
        Binarizes the intensity of the pixels.
        For Grayscale images, it's known as a real B&W.
        For RGB images, it will binarize each color channel.
        """
        canvas = self.img.get_canvas()
        pixels = np.zeros((self.img.count_pixels(), 3)).astype(np.uint8)
        # Grayscale
        f = None
        if not self.isRGB:
            f = lambda pixel: (255, 255, 255) if pixel[0] >= threshold else (0, 0, 0)
        else:  # RGB
            f = lambda pixel: (
                255 if pixel[0] >= threshold else 0,
                255 if pixel[1] >= threshold else 0,
                255 if pixel[2] >= threshold else 0,
            )
        for i, pixel in enumerate(canvas):
            pixels[i] = f(pixel)
        return Image(size=self.img.get_size(), canvas=pixels)

    def blur(self, level: int = 1) -> Image:
        """
        Blurs an img.
        """
        pixels = np.zeros((self.img.count_pixels(), 3)).astype(np.uint8)
        w, h = self.img.get_size()

        neighbours = []
        if not self.isRGB:
            mean = 0
            for y in range(h):
                for x in range(w):
                    neighbours = self.img.get_pixel_area(x, y, level)
                    mean = int(sum(pixel[0] for pixel in neighbours) / len(neighbours))
                    pixels[y * w + x] = (mean, mean, mean)
        else:
            r, g, b = 0, 0, 0
            for y in range(h):
                for x in range(w):
                    r, g, b = 0, 0, 0
                    neighbours = self.img.get_pixel_area(x, y, level)
                    for pixel in neighbours:
                        r += pixel[0]
                        g += pixel[1]
                        b += pixel[2]

                    l = len(neighbours)
                    r = int(r / l)
                    g = int(g / l)
                    b = int(b / l)
                    pixels[y * w + x] = np.array([r, g, b]).astype(np.uint8)

        return Image(size=self.img.get_size(), canvas=pixels)

    def blur_median(self, level: int = 2) -> Image:
        """
        Blurs an img.
        """
        pixels = np.zeros((self.img.count_pixels(), 3)).astype(np.uint8)
        w, h = self.img.get_size()
        if not self.isRGB:
            mean = 0
            for y in range(h):
                for x in range(w):
                    neighbours = self.img.get_pixel_area(x, y, level)
                    neighbours = np.sort(neighbours)
                    mean = neighbours[len(neighbours) // 2][0]
                    pixels[y * w + x] = np.array([mean, mean, mean]).astype(np.uint8)

        else:
            for y in range(h):
                for x in range(w):
                    neighbours: list[np.ndarray] = self.img.get_pixel_area(x, y, level)
                    neighbours = np.sort(neighbours, axis=0)
                    pixels[y * w + x] = np.array(
                        neighbours[len(neighbours) // 2]
                    ).astype(np.uint8)
        return Image(size=self.img.get_size(), canvas=pixels)

    def salt_and_pepper(self, amount: float = 1) -> Image:
        """
        Adds salt and pepper noise to an img.
        """
        from random import randint

        w, h = self.img.get_size()
        pixels = self.img.get_canvas().copy()
        perc = int((amount / 100) * self.img.count_pixels())

        for _ in range(perc // 2):
            x1, y1 = randint(0, w - 1), randint(0, h - 1)
            x2, y2 = randint(0, w - 1), randint(0, h - 1)
            pixels[y1 * w + x1] = np.array([0, 0, 0]).astype(np.uint8)
            pixels[y2 * w + x2] = np.array([255, 255, 255]).astype(np.uint8)
        return Image(size=self.img.get_size(), canvas=pixels)
