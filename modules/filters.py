from classes.image import Image
from ctypes import *


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
        f = lambda pixel: int(0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2])

        def new_pixel(pixel):
            c = f(pixel)
            return (c, c, c)

        canvas = self.img.get_canvas()
        pixels = [new_pixel(p) for p in canvas]

        return Image(size=self.img.get_size(), canvas=pixels)

    def equalize(self) -> Image:
        """
        Equalizes the histogram of an img.
        """
        pass

    def negative(self) -> Image:
        """
        Inverts the colors of an img.
        """
        canvas = self.img.get_canvas()
        pixels = []
        # Grayscale
        if not self.isRGB:
            f = lambda pixel: 255 - pixel[0]
            for pixel in canvas:
                neg = f(pixel)
                pixels.append((neg, neg, neg))
        # RGB
        else:
            f = lambda pixel: (255 - pixel[0], 255 - pixel[1], 255 - pixel[2])
            pixels = [f(pixel) for pixel in canvas]

        return Image(size=self.img.get_size(), canvas=pixels)

    def binarize(self, threshold: int = 128) -> Image:
        """
        Binarizes the intensity of the pixels.
        For Grayscale images, it's known as a real B&W.
        For RGB images, it will binarize each color channel.
        """
        canvas = self.img.get_canvas()
        pixels = []
        # Grayscale
        if not self.isRGB:
            f = lambda pixel: 255 if pixel[0] >= threshold else 0
            for pixel in canvas:
                c = f(pixel)
                pixels.append((c, c, c))

        else:  # RGB
            f = lambda pixel: (
                255 if pixel[0] >= threshold else 0,
                255 if pixel[1] >= threshold else 0,
                255 if pixel[2] >= threshold else 0,
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

        if not self.isRGB:
            for y in range(h):
                for x in range(w):
                    # Get neighbours
                    neighbours = self.img.get_pixel_area(x, y, level)
                    mean = int(sum(pixel[0] for pixel in neighbours) / len(neighbours))
                    pixels.append((mean, mean, mean))
        else:
            for y in range(h):
                for x in range(w):
                    neighbours = self.img.get_pixel_area(x, y, level)
                    r = int(sum(pixel[0] for pixel in neighbours) / len(neighbours))
                    g = int(sum(pixel[1] for pixel in neighbours) / len(neighbours))
                    b = int(sum(pixel[2] for pixel in neighbours) / len(neighbours))
                    pixels.append((r, g, b))

        return Image(size=self.img.get_size(), canvas=pixels)

    def blur_median(self, level: int = 3) -> Image:
        """
        Blurs an img.
        """
        pixels: list = []
        w = self.img.get_width()
        h = self.img.get_height()
        if not self.isRGB:
            for y in range(h):
                for x in range(w):
                    neighbours = self.img.get_pixel_area(x, y, level)
                    neighbours.sort()
                    mean = neighbours[len(neighbours) // 2][0]
                    pixels.append((mean, mean, mean))

        else:
            for y in range(h):
                for x in range(w):
                    neighbours = self.img.get_pixel_area(x, y, level)
                    neighbours.sort()
                    r = neighbours[len(neighbours) // 2][0]
                    g = neighbours[len(neighbours) // 2][1]
                    b = neighbours[len(neighbours) // 2][2]
                    pixels.append((r, g, b))

        return Image(size=self.img.get_size(), canvas=pixels)
