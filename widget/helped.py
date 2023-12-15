from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QLineEdit, QFormLayout, QCheckBox

from widget.inputinformation import InputInformation
from widget.progressbar import ProgressBar
from widget.worker import ExplorerWorker
from widget.button import Button


class Helped:
    def __init__(self):
        self.workers: list[ExplorerWorker] = []
        self.threads: list[QThread] = []

        self.inputs: dict[str, InputInformation] = {}
        self.buttons: dict[str, Button] = {}
        self.progress_bars: dict[str, ProgressBar] = {}

    def create_input(self, name, label, default_value=None, checkbox=False):
        layout = QFormLayout()
        if not checkbox:
            line_input = QLineEdit()
            if default_value is not None:
                line_input.setText(default_value)
            layout.addRow(label, line_input)
            self.inputs[name] = InputInformation(layout, line_input)
        else:
            checkbox = QCheckBox()
            checkbox.setTristate(False)
            if default_value is not None:
                checkbox.setChecked(default_value)
            layout.addRow(label, checkbox)
            self.inputs[name] = InputInformation(layout, checkbox)

        return self.inputs[name]

    def create_button(self, name, label, on_click, default_state=True):
        button = Button(label, on_click)
        if not default_state:
            button.setEnabled(default_state)
        self.buttons[name] = button
        return button

    def create_progress_bar(self, name, label, minimum, maximum, on_finish=None):
        print("Creating progress bar")
        progress_bar = ProgressBar(label, minimum, maximum, on_finish)
        print("Progress bar created")
        self.progress_bars[name] = progress_bar
        print("Progress bar added to list")
        return progress_bar

    def create_explorer_worker(self, name, download_path="", options=None):
        print(f"Creating worker (DP:{download_path})")
        worker = ExplorerWorker(name, download_path=download_path, options=options)
        print("Worker fully created")
        thread = QThread()
        print("Thread created")
        worker.moveToThread(thread)
        print("Worker moved on new thread")
        thread.start()
        self.workers.append(worker)
        self.threads.append(thread)
        print("New obj saved")
        return worker
