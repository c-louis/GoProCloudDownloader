from __future__ import annotations

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QDialog, QLabel

from widget.helped import Helped


class AppHeader(QWidget, Helped):
    """
        AppHeader Contains and control the header of the app
    """

    def __init__(self, explore, download):
        super().__init__()
        Helped.__init__(self)

        self.dialog : QDialog | None = None
        self.download_path = ""
        self.url = ""

        self.main_layout = QVBoxLayout()

        self.input_layout = QHBoxLayout()
        path = self.create_input("download_path", "Download Path")
        self.input_layout.addLayout(path.layout)
        self.input_layout.addWidget(self.create_button("select_directory", "Select Directory", self.select_folder))
        url = self.create_input("urls", "GoPro Cloud URL(s) (Separator: ;)")
        self.input_layout.addLayout(url.layout)
        self.main_layout.addLayout(self.input_layout)

        self.explorer_layout = QHBoxLayout()
        self.explorer_layout.addWidget(self.create_button("explore", "Explore link", explore))
        self.explorer_layout.addWidget(self.create_button("download_all", "Download all", download, False))
        self.explorer_layout.addWidget(self.create_button("advanced_settings", "Advanced Settings", self.advanced_settings_popup))
        self.main_layout.addLayout(self.explorer_layout)

        self.setLayout(self.main_layout)

        self.options = {
            "steps": 30,  # Steps of scrolling on a page, 30 is good for up to 200 elements at speed 1
            "speed": 1,  # Divide sleeps by x, use at your own risk
            "sound": False,
            "headless": True,
            "load_thumbnail": True,
        }

    def select_folder(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)

        if dialog.exec_():
            dirs = dialog.selectedUrls()
            if len(dirs) > 0:
                selected_path = dirs[0].path()
                self.inputs["download_path"].input.setText(selected_path)
        return None

    def get_urls(self):
        if len(self.inputs["urls"].input.text()) == 0:
            return None
        urls = self.inputs["urls"].input.text().split(";")
        return urls

    def get_download_path(self):
        return self.inputs["download_path"].input.text().replace("/", "\\").lstrip('\\')

    def toggle_buttons(self, state):
        self.buttons["explore"].setEnabled(state)
        self.buttons["download_all"].setEnabled(state)
        print(f"Button {state}")

    def advanced_settings_popup(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Advanced Settings")

        dialog_layout = QVBoxLayout()

        step_explained = QLabel()
        step_explained.setText("Steps of scrolling on a page, 30 is good for up to 200 elements at speed 1")
        dialog_layout.addWidget(step_explained)
        steps_input = self.create_input("steps", "Steps", default_value=str(self.options["steps"]))
        dialog_layout.addLayout(steps_input.layout)

        speed_explained = QLabel()
        speed_explained.setText("Speeds divide sleeps by X, use at your own risk")
        dialog_layout.addWidget(speed_explained)
        speed_input = self.create_input("speed", "Speed", default_value=str(self.options["speed"]))
        dialog_layout.addLayout(speed_input.layout)

        sound_explained = QLabel()
        sound_explained.setText("Chrome plays sound of your videos while we look for them")
        dialog_layout.addWidget(sound_explained)
        sound_input = self.create_input("sound", "Chrome sound", checkbox=True, default_value=self.options["sound"])
        dialog_layout.addLayout(sound_input.layout)

        headless_explained = QLabel()
        headless_explained.setText("False is showing the browser working")
        dialog_layout.addWidget(headless_explained)
        headless_input = self.create_input("headless", "Headless", checkbox=True, default_value=self.options["headless"])
        dialog_layout.addLayout(headless_input.layout)

        thumbnail_explained = QLabel()
        thumbnail_explained.setText("Load medias thumbnail (all might not be available due to GoPro")
        dialog_layout.addWidget(thumbnail_explained)
        thumbnail_input = self.create_input("load_thumbnail", "Thumbnail", checkbox=True,
                                            default_value=self.options["load_thumbnail"])
        dialog_layout.addLayout(thumbnail_input.layout)
        dialog_layout.addWidget(self.create_button("dialog_ok", "Save", self.dialog_save))
        self.dialog = dialog

        dialog.setLayout(dialog_layout)
        dialog.exec()

    def dialog_save(self):
        self.options["steps"] = int(self.inputs["steps"].input.text())  # Steps of scrolling on a page, 30 is good for up to 200 elements at speed 1
        self.options["speed"] = int(self.inputs["speed"].input.text())  # Divide sleeps by x, use at your own risk
        self.options["sound"] = bool(self.inputs["sound"].input.checkState())
        self.options["headless"] = bool(self.inputs["headless"].input.checkState())
        self.options["load_thumbnail"] = bool(self.inputs["load_thumbnail"].input.checkState())
        self.dialog.close()

