import io
import urllib.request

from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

from PIL import Image


class WebImage(QLabel):
    def __init__(self, url=None, data=None):
        super().__init__()
        try:
            if url is not None:
                data = urllib.request.urlopen(url).read()
            self.image = QImage()
            self.image.loadFromData(data)
            self.pixmap = QPixmap(self.image)
            self.pixmap = self.pixmap.scaledToWidth(
                self.pixmap.width() if self.pixmap.width() < 300 else 350,
            )
            self.setPixmap(self.pixmap)
        except:
            pass
