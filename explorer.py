import argparse
import io
import random
import re
import time
import json
import threading

from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import ChromiumOptions


class GoProCloudContentInformation:
    def __init__(self, elem):
        self.elem = elem
        self.url = elem.get_attribute("href")
        style = elem.find_element(By.XPATH, "*[1]/*[1]/*[1]").get_attribute("style")
        m = re.search("url\(\"(?P<thumbnail>.*)\"\)", style)
        if m is not None and "thumbnail" in m.groupdict():
            self.thumbnail_url = m.group('thumbnail')
        else:
            self.thumbnail_url = None


class Explorer:
    def __init__(self, headless=False, download_path="", sound=False, steps=30, speed=1):
        self.steps = steps
        self.speed = speed
        print(f"Speed({self.speed} Steps:{self.steps})")

        self.options = webdriver.ChromeOptions()
        print(f"Creating Explorer with DDD: {download_path}")
        self.options.add_experimental_option('prefs', {
            "download.default_directory": download_path})
        print(f"Headless: {headless}")
        if headless:
            self.options.add_argument('--headless=new')
        if not sound:
            self.options.add_argument("--mute-audio")
        self.elements = []

        self.threads = []

    def set_download_path(self, download_path):
        self.options.add_experimental_option('prefs', {"download.default_directory": download_path})

    def explore(self, url, steps=30, on_progress=None, use_threading=True):
        print(f'Exploring: {url}, will take approximately {self.steps / 2 + 5} seconds')
        if use_threading:
            self.threads.append(threading.Thread(target=self.__inner_explore, args=(url, self.steps, on_progress)))
            self.threads[-1].start()
        else:
            self.__inner_explore(url, self.steps, on_progress)

    def __inner_explore(self, url, steps, on_progress):
        print(f"Starting explore Exploring : {url}")
        driver = webdriver.Chrome(self.options)
        print("Driver created")
        driver.get(url)
        print("Page got")
        time.sleep(2/self.speed)
        print("Slept")
        if on_progress is not None:
            print("Progress !")
            on_progress((1 / 34 * 4)*100)
        for i in range(self.steps):
            print(f"Step : {i}")
            driver.execute_script(f'window.scrollBy(0,document.body.scrollHeight/{self.steps})', "")
            print("Scroll done")
            time.sleep(.5/self.speed)
            if on_progress is not None:
                print(f"Progress !")
                on_progress((1 / 34 * (i + 4))*100)
                print("End progress")
        elems = driver.find_elements(By.CSS_SELECTOR, 'div > div > a')
        gopro_information = [GoProCloudContentInformation(elem) for elem in elems]
        self.elements.extend(gopro_information)
        print(f'Found : {len(gopro_information)}, Total elements: {len(self.elements)}')
        on_progress(100)
        driver.quit()

    def explore_all(self, urls, steps=30):
        self.elements = []
        for url in urls:
            self.explore(url, self.steps)
        return self.elements

    def download_all(self, elements, on_download_started=None, on_download_progress=None):
        driver = webdriver.Chrome(self.options)
        for elem in elements:
            self.download(driver, elem, on_download_started, on_download_progress)

    def download(self, driver, elem: GoProCloudContentInformation, on_download_started=None, on_download_progress=None):
        print(f"Downloading {elem.url}, should take up to 3 seconds to start")
        driver.get(elem.url)
        time.sleep(2/self.speed)
        driver.find_element(By.ID, "1").click()
        time.sleep(.5/self.speed)
        driver.find_element(By.CSS_SELECTOR, "li.download-media > a").click()
        time.sleep(.5/self.speed)
        if on_download_started is not None:
            on_download_started(elem)

        last_progression = 0
        if len(driver.window_handles) != 1:
            driver.switch_to.window(driver.window_handles[-1])
        while True:
            print(f"window handled: {len(driver.window_handles)}")
            if len(driver.window_handles) == 1:
                print("Opening window !")
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get("chrome://downloads")
            time.sleep(.2/self.speed)
            manager = driver.find_element(By.TAG_NAME, "downloads-manager")
            print(manager)
            mc = manager.shadow_root.find_element(By.ID, "mainContainer")
            print(mc)
            downloaded_elem = mc.find_element(By.TAG_NAME, "downloads-item")
            print(downloaded_elem)
            if downloaded_elem is None:
                print(f"Download doesnt {elem.url} seems to have started !")
                continue
            value = downloaded_elem.shadow_root.find_element(By.ID, "progress").get_attribute("value")
            print(f"LP:{last_progression}|value:{value}")
            if on_download_progress is not None and value != last_progression:
                print("Sending progress of download")
                last_progression = value
                on_download_progress(value)
                print("Progression sent")
            if int(last_progression) == 100:
                print("Switch to old window")
                driver.switch_to.window(driver.window_handles[0])
                break
