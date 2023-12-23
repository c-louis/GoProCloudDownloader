import argparse
import io
import random
import re
import time
import json
import threading
import requests
import queue
import time

from typing import Optional

import urllib

class GoProCloudContentInformationV2:
    def __init__(self, elem):
        self.elem = elem
        self.id = elem["id"]
        self.token = elem["token"]
        self.camera = elem["camera_model"]
        self.size = elem["file_size"]
        self.filename = elem["filename"]
        


class ExplorerV2:
    def __init__(self, z, zms, zmf, q, sd, dr, download_path="", debug=False, use_threading=True):
        self.use_threading = use_threading
        self.download_path = download_path
        self.elements = []
        self.threads = []
        self.semaphore = threading.Semaphore(sd)
        self.progress_bars_owned = []

        self.zip = z
        self.zip_max_size = zms
        self.zip_max_file = zmf
        self.quality = q
        self.simultanate_download = sd
        self.dry_run = dr
        self.debug = debug
        
    def explore(self, url, on_progress=None):
        res = requests.get(url)
        res = re.search(r"__reflectData=(?P<json>.*);</script>", res.text)
        data = json.loads(res.group("json"))
        medias = data["collectionMedia"]
        elems = []
        for media in medias:
            elems.append(GoProCloudContentInformationV2(media))
        print(f"Explored: {url} found: {len(elems)} medias")
        self.elements.extend(elems)
        if on_progress is not None:
            on_progress(100)
        pass

    def explore_all(self, urls):
        self.elements = []
        if not self.use_threading:
            for url in urls:
                self.explore(url, self.steps)
        else:
            self.threads = []
            for url in urls:
                thread = threading.Thread(target=self.explore, args=(url,))
                self.threads.append(thread)
                thread.start()

            for thread in self.threads:
                thread.join()
            self.threads = []
        print(f"Done exploring all, total medias: {len(self.elements)}")
        return self.elements
    
    def get_medias_list(self):
        return self.elements

    def get_medias_total_size(self):
        return sum(elem.size for elem in self.elements if elem.size is not None)
    
    def split_for_zip(self, elements=None):
        if elements is None:
            elements = self.elements
        ll = []
        l = []
        
        for file in elements:
            if file.size is None:
                continue
            # Exception 1 zip dl ?
            if len(l) == 0 and file.size > self.zip_max_size:
                ll.append(file)
                continue
            # Calculate l current size
            ls = 0
            for f1 in l:
                ls = ls + f1.size
            # Check if size of l (ls) + possibly size of file fits under zip_max_size
            if ls + file.size > self.zip_max_size or len(l) + 1 >= self.zip_max_file:
                ll.append(l)
                l = []
                ls = 0
            # Array had enough size, add file
            l.append(file)
        if len(l) != 0:
            ll.append(l)
        return ll


    def download_all(self, elements:list[GoProCloudContentInformationV2]=None, download_callbacks=[]):
        self.progress_bars_owned = [False] * self.simultanate_download

        if elements is None:
            elements = self.elements
        if self.debug:
            print(f"Download of {len(elements)} requested")
        elements.sort(key=lambda elem: elem.size if elem.size is not None else 0)

        if self.quality == "hd" and self.zip is True:
            ll = self.split_for_zip(elements)
            if self.debug:
                print(f"\twill download in {len(ll)} different download")
            packID = 0
            for l in ll:
                if isinstance(l, GoProCloudContentInformationV2):
                    download_thread = threading.Thread(target=self.download, args=(None,l.id, self.quality, None, l.size, download_callbacks))
                    self.threads.append(download_thread)
                    continue

                # https://api.gopro.com/media/x/zip/source?ids=
                # Download files HD in zips according to zip rules zip_max_size, zip_max_files
                url = f"https://api.gopro.com/media/x/zip/source?ids={','.join(e.id for e in l)}"
                total_size = sum(elem.size for elem in l)
                download_thread = threading.Thread(target=self.download, args=(url, None, self.quality, str(packID), total_size, download_callbacks))
                self.threads.append(download_thread)
                packID += 1
        else:
            # Download files one by one without zip for source quality
            for file in elements:
                download_thread = threading.Thread(target=self.download, args=(None,file.id, self.quality, None, file.size, download_callbacks))
                self.threads.append(download_thread)

        for thread in self.threads:
            thread.start()

    def download(self, url=None, mediaID=None, quality=None, packID=None, size=None, download_callbacks=[]):
        with self.semaphore:
            pbi = None
            if self.debug:
                print(f"{self.progress_bars_owned} : {pbi}")
            for idx, pbs in enumerate(self.progress_bars_owned):
                if not pbs:
                    self.progress_bars_owned[idx] = True
                    pbi = idx
                    break
            if "start" in download_callbacks:
                download_callbacks["start"](pbi, f"pack.{packID}.zip" if url is not None else f"{mediaID}.{quality}", size)
            if url is None and mediaID is None or (mediaID is not None and quality is None) or (url is not None and packID is None):
                return
            if url is not None:
                self.__download_url(url, f"pack.{packID}.zip", pbi, size, download_callbacks)
                self.progress_bars_owned[idx] = False
                return
            self.__download_mediaID(mediaID, quality, pbi, size, download_callbacks)
            self.progress_bars_owned[idx] = False
            return
        
    def __download_url(self, url, filename, progress_bar_id, size, download_callbacks=[]):
        if self.dry_run:
            print(f"DryRun: dd {url} to filename {filename} events : {download_callbacks}")
            return
        def reporthook(count, block_size, total_size):
            if "progress" in download_callbacks:
                download_callbacks["progress"](progress_bar_id, count, block_size, total_size, size)

        if self.debug:
            print(f"Downloading {self.download_path}{filename}")
            print(url)
        urllib.request.urlretrieve(url, filename=f"{self.download_path}{filename}", reporthook=reporthook)
        if "stop" in download_callbacks:
            download_callbacks["stop"](progress_bar_id, url)
        return

    def __download_mediaID(self, mediaID, quality, progress_bar_id, size, download_callbacks=[]):
        resp = requests.get(f"https://api.gopro.com/media/{mediaID}/download")
        data = json.loads(resp.text)
        variations = data["_embedded"]["variations"]
        for var in variations:
            if (quality == "hd" and var["label"] == "high_res_proxy_mp4") or (quality == "source" and var["label"] == "source") or var["type"] == "jpg":
                resp = requests.head(var["head"])
                if "Content-Length" in resp.headers:
                    size = int(resp.headers["Content-Length"])
                    if "start" in download_callbacks:
                        download_callbacks["start"](progress_bar_id, f"{mediaID}.{quality}", size)
                self.__download_url(var["url"], f"{mediaID}.{quality}.{var['type']}", progress_bar_id, size, download_callbacks)
                break
        else:
            if "stop" in download_callbacks:
                download_callbacks["stop"](progress_bar_id, f"Not D: {mediaID}")
