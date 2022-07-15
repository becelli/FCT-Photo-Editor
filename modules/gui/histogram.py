import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtGui import QImage
import modules.gui.qt_override as qto
from modules.filters import Filters


def display_histogram(image) -> None:
    hist, bins = calculate_image_histogram(image)
    plt.bar(bins[:-1], hist, width=2, color="black")
    plt.title("Histogram")
    plt.show()


def calculate_image_histogram(image) -> tuple[np.ndarray, np.ndarray]:
    gray_image = get_gray_image(image)
    image_pixels = get_array_of_pixels_from_image(gray_image)
    hist, bins = np.histogram(image_pixels, bins=255, range=(0, 255))
    hist = hist / np.max(hist)  # Normalizing
    return hist, bins


def get_array_of_pixels_from_image(image: QImage) -> np.ndarray:
    w, h = image.width(), image.height()
    pixels = np.array(image.bits().asarray(w * h * 4))[::4]
    print(pixels)
    return pixels


def get_gray_image(canvas) -> QImage:
    f = Filters(img=qto.get_image_from_canvas(canvas))
    image: QImage = f.grayscale()
    return image
