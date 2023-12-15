import time

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QProgressBar, QWidget, QLabel, QVBoxLayout


class ProgressBar(QWidget):
    def __init__(self, label, minimum, maximum, on_finish=None):
        super().__init__()
        self.label = QLabel()
        self.label.setText(label)

        self.bar = QProgressBar()
        self.bar.setRange(minimum, maximum)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.bar)
        self.setLayout(self.layout)

        self.on_finish = on_finish

    def set_value(self, value):
        print(f"Set value of {self.label.text()} to {value} max is : {self.bar.maximum()}")
        self.bar.setValue(value)
        print("Value set")
        if value == self.bar.maximum():
            print("Value is max")
            if self.on_finish is not None:
                print("Call on finish")
                self.on_finish()
