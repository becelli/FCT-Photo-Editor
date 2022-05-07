from classes.image import Image
from ctypes import *


class Filters:
    def __init__(self, img: Image):
        self.img: Image = img

    def grayscale(self, isCie=False) -> Image:
        """
        Converts an img to a grayscale version.
        """
        canvas = self.img.get_canvas()
        # Average of the RGB values
        f = (
            lambda pixel: int(0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2])
            if not isCie
            else int(sum(pixel) / 3)
        )
        npixel = lambda pixel: (f(pixel), f(pixel), f(pixel))
        pixels = [npixel(pixel) for pixel in canvas]
        return Image(size=self.img.get_size(), canvas=pixels)

    def expand_contrast(self) -> Image:
        """
        Expands the contrast of an img.
        """
        canvas = self.img.get_canvas()
        pixels = []
        # Expand the contrast
        if not self.img.isRGB:
            minimum = min(canvas)[0]
            maximum = max(canvas)[0]
            # do not divide by zero
            f = lambda pixel: int(
                ((pixel - minimum + 1) * 255) / (maximum - minimum + 1) % 256
            )
            for pixel in canvas:
                r = f(pixel[0])
                pixels.append((r, r, r))
        else:
            minimum = min(canvas)
            maximum = max(canvas)
            f = lambda pixel, i: int(pixel[i] * 255 / ((maximum[i] - minimum[i]) + 1))
            npixel = lambda pixel: (f(pixel, 0), f(pixel, 1), f(pixel, 2))
            pixels = [npixel(pixel) for pixel in canvas]

        return Image(size=self.img.get_size(), canvas=pixels)

    def negative(self) -> Image:
        """
        Inverts the colors of an img.
        """
        canvas = self.img.get_canvas()
        pixels = []
        if not self.img.isRGB:
            f = lambda pixel: 255 - pixel[0]
            for pixel in canvas:
                pixels.append((f(pixel), f(pixel), f(pixel)))
        else:
            f = lambda pixel: (255 - pixel[0], 255 - pixel[1], 255 - pixel[2])
            pixels = [f(pixel) for pixel in canvas]
        return Image(size=self.img.get_size(), canvas=pixels)

    def binarize(self, threshold: int = 128) -> Image:
        """
        Binarizes an img.
        """
        canvas = self.img.get_canvas()
        pixels = []
        if not self.img.isRGB:
            f = lambda pixel: 255 if pixel[0] > threshold else 0
            for pixel in canvas:
                c = f(pixel)
                pixels.append((c, c, c))
        else:
            f = lambda pixel: (
                255 if pixel[0] > threshold else 0,
                255 if pixel[1] > threshold else 0,
                255 if pixel[2] > threshold else 0,
            )
            pixels = [f(pixel) for pixel in canvas]
        return Image(size=self.img.get_size(), canvas=pixels)

    def blur(self, level: int = 2) -> Image:
        """
        Blurs an img.
        """
        pixels = []
        w = self.img.get_width()
        h = self.img.get_height()

        # if not self.img.isRGB:
        for y in range(h):
            for x in range(w):
                # Get neighbours
                neighbours = self.img.get_pixel_area(x, y, level)
                mean = int(sum(pixel[0] for pixel in neighbours) / len(neighbours))
                pixel = (mean, mean, mean)
                pixels.append(pixel)
        return Image(size=self.img.get_size(), canvas=pixels)

    def blur_c(self, level: int = 2) -> Image:
        """
        Blurs an img.
        """
        pixels = []
        w = self.img.get_width()
        h = self.img.get_height()

        for y in range(h):
            for x in range(w):
                # Get neighbours
                neighbours = self.img.get_pixel_area(x, y, level)
                mean = int(sum(pixel[0] for pixel in neighbours) / len(neighbours))
                pixel = (mean, mean, mean)
                pixels.append(pixel)
        return Image(size=self.img.get_size(), canvas=pixels)
