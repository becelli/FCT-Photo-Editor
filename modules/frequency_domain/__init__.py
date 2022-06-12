from modules.qt_override import *
from modules.filters import Filters

# from modules.qt_override import QObjects, QChildWindow


class FrequencyDomain:
    def __init__(self, parent, image):
        self.window = QChildWindow(parent, "Frequency Domain Tools", 1280, 720)
        self.window.show()

        Filters(image).discrete_cousine_transform()
