from PyQt5.QtWidgets import QPushButton


class Button(QPushButton):
    def __init__(self, label, on_click):
        super().__init__(label)
        self.clicked.connect(on_click)
