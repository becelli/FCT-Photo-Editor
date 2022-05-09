import matplotlib.pyplot as plt
import numpy as np


def histogram(image: np.ndarray) -> None:
    """
    Plot the histogram of an image.
    """
    # Change figsize
    plt.rcParams["figure.figsize"] = (20, 3)
    red, green, blue = image.T
    redw = 100 * np.ones_like(red) / np.sum(red)
    greenw = np.ones_like(green) / len(green)
    bluew = np.ones_like(blue) / len(blue)
    mean = np.mean(image, axis=1)

    # Make y to max 1. This is to avoid the plot being too high.
    plt.subplot(1, 4, 1)
    plt.ylim(0, 1)
    plt.hist(red, bins=256, weights=redw, color="red")
    plt.title("Red")
    # plt.ylabel("Frequency")
    # Green channel
    plt.subplot(1, 4, 2)
    plt.ylim(0, 1)
    plt.hist(green, bins=256, weights=greenw, color="green")
    plt.title("Green")
    # plt.ylabel("Frequency")
    # Blue channel
    plt.subplot(1, 4, 3)
    plt.ylim(0, 1)
    plt.hist(blue, bins=256, weights=bluew, color="blue")
    plt.title("Blue")
    # plt.ylabel("Frequency")
    # All channels
    plt.subplot(1, 4, 4)
    plt.hist(mean, bins=256, color="black")
    plt.title("All")
    plt.ylabel("Frequency")
    # Show the plot
    plt.show()


# plt.hist(image.ravel(), bins=256, range=(0.0, 256.0), fc="k", ec="k")

import random

n = 320 * 240
image = np.zeros((n, 3), dtype=np.uint8)
for i in range(n):
    # Random pixel
    image[i] = [random.randint(0, 255) for _ in range(3)]

histogram(image)
