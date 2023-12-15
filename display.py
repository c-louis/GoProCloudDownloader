import sys

from PyQt5.QtCore import QObject, pyqtSlot

from explorer import GoProCloudContentInformation

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, \
    QSizePolicy, QScrollArea

from widget.flowlayout import FlowLayout
from widget.helped import Helped
from widget.image import WebImage
from widget.layouts.head import AppHeader


class Display(QObject, Helped):
    def __init__(self):
        Helped.__init__(self)
        super().__init__()
        self.last_data = None

        self.app = QApplication([])
        self.app.setStyle('Fusion')

        # Init main window
        self.window = QWidget()
        self.window.setWindowTitle("GoPro Cloud Downloader")
        self.window.resize(1100, 700)
        self.window_layout = QVBoxLayout()
        # End main

        # Init inputs widget
        self.head = AppHeader(explore=self.explore, download=self.download_all)
        self.window_layout.addWidget(self.head)
        # End inputs

        # Init progress widget
        self.progress_layout = QHBoxLayout()
        self.window_layout.addLayout(self.progress_layout)
        # End progress layout

        # Init content widget
        widget = QWidget()
        self.content_widget_layout = FlowLayout()
        widget.setLayout(self.content_widget_layout)
        scrollArea = QScrollArea()
        scrollArea.setWidget(widget)
        scrollArea.setWidgetResizable(True)
        scrollArea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.window_layout.addWidget(scrollArea)
        # End content

        # Set layout of window
        self.window.setLayout(self.window_layout)

        # Start app
        self.window.show()
        sys.exit(self.app.exec_())

    """ widget creation part """
    def create_explorer_worker(self, name, download_path="", options=None):
        worker = Helped.create_explorer_worker(self, name, download_path, options=options)
        worker.on_progress.connect(self.progress_bar_update)
        worker.on_image_loaded.connect(self.add_image)
        worker.on_download_started.connect(self.download_started)
        return worker


    """ Buttons actions """
    def explore(self):
        print("Explore!")
        urls = self.head.get_urls()
        if len(urls) == 0:
            return None
        print(f"Got url {urls}")
        self.head.toggle_buttons(False)
        self.clear_progress_bar()
        print("Progress bar cleared")
        for url in urls:
            print(f"Exploring {url}")
            bar = self.create_progress_bar(f"pb_{url}", url, 0, 100, self.on_explore_finish)
            print("Progress bar created")
            self.progress_layout.addWidget(bar)
            print("Progress bar added")
            worker = self.create_explorer_worker(f"pb_{url}", options=self.head.options)
            print("worker created !")
            worker.explore_launcher.emit(url, 1)
            print("Exploration starting")

    def download_all(self):
        self.head.toggle_buttons(False)
        data = []
        for w in self.workers:
            data.extend(w.explorer.elements)

        self.clear_progress_bar()
        total_downloaded = self.create_progress_bar("downloaded_total",
                                                    f"Total Downloaded",
                                                    0, len(data))
        total_downloaded.bar.setFormat("%v/%m (%p%)")
        self.progress_layout.addWidget(total_downloaded)
        print("Added downloaded_total")

        nb = self.create_progress_bar("current_download", "Current Download", 0, 100)
        self.progress_layout.addWidget(nb)
        print("Added current_download")

        worker = self.create_explorer_worker("downloader", self.head.get_download_path(), options=self.head.options)
        worker.download_launcher.emit(data)

    """ QT Slots """
    @pyqtSlot(str, float)
    def progress_bar_update(self, progress_bar_name, progress):
        print(f"On progress bar update {progress_bar_name}, value {progress}")
        if progress_bar_name not in self.progress_bars:
            print("Progress bar dont exist !!")
            return
        if progress is None:
            progress = self.progress_bars[progress_bar_name].bar.value() + 1
            if progress == 0:
                progress = 1
        self.progress_bars[progress_bar_name].set_value(progress)
        print("Emitted")

    @pyqtSlot(bytes)
    def add_image(self, data: bytes):
        print("Adding image")
        self.content_widget_layout.addWidget(WebImage(url=None, data=data))
        self.progress_bar_update("img_load_progress", progress=None)
        print("Added image")

    @pyqtSlot(str)
    def download_started(self, elem: str):
        print("Update all total")
        self.progress_bar_update("downloaded_total", progress=None)
        print("Current download updated to value 0")
        self.progress_bars["current_download"].set_value(0)
        print("Done download_started")

    """ On finish functions """
    def on_explore_finish(self):
        nb_bars = 0
        progress_total = 0
        for key, pb in self.progress_bars.items():
            if key.startswith("pb_"):
                nb_bars += 1
                progress_total += pb.bar.value()
        print(nb_bars)
        print(progress_total)
        if nb_bars * 100 == progress_total:
            print("Starting data exploration")
            data = []
            for worker in self.workers:
                data.extend(worker.explorer.elements)
            n_data = []
            for d in data:
                if d.thumbnail_url is not None:
                    n_data.append(d)

            img_load_progress = self.create_progress_bar("img_load_progress", "Loading Progress", 0, len(n_data), self.on_loading_finish)
            self.progress_layout.addWidget(img_load_progress)

            print("Set data")
            if self.head.options["load_thumbnail"]:
                self.set_data(n_data)
            else:
                self.on_loading_finish()
            print("Data set")

    def on_loading_finish(self):
        data_count = 0
        for worker in self.workers:
            data_count += len(worker.explorer.elements)
        self.head.toggle_buttons(True)
        self.head.buttons["download_all"].setText(f"Download All ({data_count})")

    def on_download_finish(self):
        self.head.toggle_buttons(True)

    def set_data(self, n_data: list[GoProCloudContentInformation]):
        chunk_size = int(len(n_data) / 3)
        chunked_list = []

        for i in range(0, len(n_data), chunk_size):
            chunked_list.append(n_data[i:i + chunk_size])
        t_len = 0
        for l in chunked_list:
            t_len += len(l)
        print(f"Tlen: {t_len}, n_data: {n_data}, thread: {len(chunked_list)}")
        for data_list in chunked_list:
            worker = None
            for w in self.workers:
                if w.busy:
                    continue
                worker = w
                print("Using exising worker")
            if worker is None:
                print("Created new data_loader worker")
                worker = self.create_explorer_worker("data_loader", options=self.head.options)
            print("Emit data_launcher function")
            worker.data_launcher.emit(data_list)

    """ Clearing content """
    def clear_progress_bar(self):
        for i in reversed(range(self.progress_layout.count())):
            self.progress_layout.itemAt(i).widget().setParent(None)
        self.progress_bars = {}
        print("Cleared progress bar")

    def clear_content(self):
        for i in reversed(range(self.content_widget_layout.count())):
            self.content_widget_layout.itemAt(i).widget().setParent(None)
