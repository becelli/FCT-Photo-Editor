class Image:
    def __init__(self, size: list, canvas: list) -> None:
        self.size = size
        self.canvas = canvas

    def get_pixel(self, x: int, y: int) -> list:
        """
        Returns the RGB values of a pixel.
        """
        # y * width + x
        return self.canvas[y * self.size[0] + x]

    def set_pixel(self, x: int, y: int, rgb: list) -> None:
        """
        Sets the RGB values of a pixel.
        """
        self.canvas[y * self.size[0] + x] = rgb

    def get_width(self) -> int:
        """
        Returns the width of the image.
        """
        return self.size[0]

    def get_height(self) -> int:
        """
        Returns the height of the image.
        """
        return self.size[1]

    def get_size(self) -> list:
        """
        Returns the size of the image.
        """
        return self.size

    def get_canvas(self) -> list:
        """
        Returns the data of the image.
        """
        return self.canvas

    def get_pixel_area(self, x: int, y: int, level: int) -> list:
        """
        Returns the RGB values of the neighbouring pixels and the pixel itself.
        """
        w = self.get_width()
        h = self.get_height()
        neighbours = []
        for i in range(x - level, x + level + 1):
            for j in range(y - level, y + level + 1):
                if i >= 0 and i < w and j >= 0 and j < h:
                    neighbours.append(self.get_pixel(i, j))
        return neighbours

    def get_histogram(self) -> dict:
        """
        Returns the histogram of the image.
        """
        histogram = {}
        for pixel in self.canvas:
            if pixel not in histogram:
                histogram[pixel] = 1
            else:
                histogram[pixel] += 1
        return histogram
