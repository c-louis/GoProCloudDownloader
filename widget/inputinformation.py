from __future__ import annotations

from PyQt5.QtWidgets import QFormLayout, QLineEdit, QCheckBox


class InputInformation:
    def __init__(self, layout, iinput):
        self.layout: QFormLayout = layout
        self.input: QLineEdit | QCheckBox = iinput
