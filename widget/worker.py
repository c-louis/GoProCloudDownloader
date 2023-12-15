import urllib

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

from explorer import Explorer, GoProCloudContentInformation
from widget.image import WebImage


class ExplorerWorker(QObject):
    explore_launcher = pyqtSignal(str, int)
    data_launcher = pyqtSignal(list)
    download_launcher = pyqtSignal(list)

    on_progress = pyqtSignal(str, float)
    on_image_loaded = pyqtSignal(bytes)

    on_download_started = pyqtSignal(str)

    def __init__(self, name, download_path="", options=None):
        super().__init__()
        print("Worker creation")
        self.explore_launcher.connect(self.explore)
        self.data_launcher.connect(self.data_load)
        self.download_launcher.connect(self.download_all)
        print("Launcher connected")
        self.name = name
        self.download_path = download_path

        print(f"Orker Options: {options}")
        headless = True if options is None or "headless" not in options else options["headless"]
        sound = False if options is None or "sound" not in options else options["sound"]
        steps = 30 if options is None or "steps" not in options else options["steps"]
        speed = 1 if options is None or "speed" not in options else options["speed"]
        print(f"Headless: {headless} speed {speed}")
        self.explorer = Explorer(headless=headless, sound=sound, steps=steps, speed=speed, download_path=download_path)
        print("Explorer created")
        self.busy = False

    @pyqtSlot(str, int)
    def explore(self, url, steps):
        self.busy = True
        self.explorer.explore(url, steps, self.on_progress_middle, use_threading=False)
        self.busy = False

    @pyqtSlot(list)
    def data_load(self, infos: list[GoProCloudContentInformation]):
        self.busy = True
        print("Loading images")
        for info in infos:
            print(info.url)
            if info.thumbnail_url is None:
                continue
            print("Will load image")
            try:
                data = urllib.request.urlopen(info.thumbnail_url).read()
            except:
                print("Exception")
                self.on_progress.emit("img_load_progress", progress=None)
                continue
            print("Before event")
            self.on_image_loaded.emit(data)
            print("Event sended !")
        self.busy = False

    @pyqtSlot(list)
    def download_all(self, data: list[GoProCloudContentInformation]):
        self.busy = True
        self.explorer.download_all(data, self.on_download_started_middle, self.on_download_progress_middle)
        self.busy = False

    def on_progress_middle(self, value):
        print("On Progress middle")
        self.on_progress.emit(self.name, value)

    def on_download_started_middle(self, elem):
        print("Sent download_started")
        self.on_download_started.emit(elem.url)

    def on_download_progress_middle(self, progress):
        print(f"Middle Adding to Current Download {progress} {type(progress)}")
        self.on_progress.emit("current_download", int(progress))
