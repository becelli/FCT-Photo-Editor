import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel
import modules.gui.qt_override as qto
from modules.filters import Filters
import os


def display_histogram(parent, image) -> None:
    hist, bins = calculate_image_histogram(image)
    plt.figure(figsize=(10, 5))
    plt.style.use("ggplot")
    plt.bar(bins[:-1], hist, width=2, color="black")
    plt.title("Histogram")
    plt.xlabel("Pixel value")
    plt.ylabel("Frequency (normalized)")
    plt.savefig("histogram.png", dpi=76)
    img = QPixmap("histogram.png")
    os.remove("histogram.png")
    display_on_screen(parent, img)


def display_on_screen(parent, pixmap) -> None:
    window = qto.QChildWindow(parent, "Histogram", 765, 400)
    window.setStyleSheet("background-color: white;")
    grid = qto.QGrid()
    label = QLabel()
    label.setPixmap(pixmap)
    grid.addWidget(label, 0, 0)
    grid.setRowStretch(10, 1)
    grid.setColumnStretch(2, 1)
    qto.display_grid_on_window(window, grid)


def calculate_image_histogram(image) -> tuple[np.ndarray, np.ndarray]:
    gray_image = get_gray_image(image)
    image_pixels = get_array_of_pixels_from_image(gray_image)
    hist, bins = np.histogram(image_pixels, bins=255, range=(0, 255))
    hist = hist / np.max(hist)  # Normalizing
    return hist, bins


def get_array_of_pixels_from_image(image: QImage) -> np.ndarray:
    w, h = image.width(), image.height()
    pixels = np.array(image.bits().asarray(w * h * 4))[::4]
    return pixels


def get_gray_image(canvas) -> QImage:
    f = Filters(img=qto.get_image_from_canvas(canvas))
    image: QImage = f.grayscale()
    return image
