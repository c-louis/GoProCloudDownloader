from tqdm import tqdm

def check_url(url):
    if not url.startswith("https://gopro.com/v/"):
        return False, f"'{url}' doesnt seems to be a valid gopro url"
    return True, None

def dc_text_start(progress_bar_id, url, known_size):
    print(f"Started a download ({progress_bar_id}): {url} or size: {known_size}")

def dc_text_progress(progress_bar_id, count, block_size, total_size, known_size):
    print(f"Progress of {progress_bar_id}:")
    print(f"\tBlocks downloaded: {count}")
    print(f"\tSize downloaded: {count * block_size}")
    print(f"\tTotal size (+known_size): {total_size} ({known_size})")

def dc_text_stopped(progress_bar_id, url):
    print(f"Stopped {url} ({progress_bar_id})")

dc_text = {
    "start": dc_text_start,
    "progress": dc_text_progress,
    "stop": dc_text_stopped
}

class ProgressBarUtils:
    def __init__(self, progress_bar_count, media_count, total_size):
        self.progress_bar_count = progress_bar_count
        self.progress_bar : list[tqdm] = []
        self.total_progress_bar : tqdm = tqdm(total=media_count, unit="media", colour="red")
        self.total_progress_bar.set_description("Files Downloaded")
        self.total_size_progress_bar : tqdm = tqdm(total=total_size, unit="b", unit_divisor=1024, unit_scale=True, colour="green")
        self.total_size_progress_bar.set_description("Size Downloaded ")
        self.last_progress_bar_block = []

        for i in range(progress_bar_count):
            self.progress_bar.append(tqdm(total=100, unit_scale=True, unit_divisor=1024, unit="b"))
            self.last_progress_bar_block.append(0)
    
    def on_start(self, progress_bar_id, url, size):
        self.progress_bar[progress_bar_id].reset(total=size if size is None or size == 0 else size)
        self.progress_bar[progress_bar_id].set_description(url)
        self.last_progress_bar_block[progress_bar_id] = 0

    def on_stop(self, progress_bar_id, url):
        self.total_size_progress_bar.update(self.progress_bar[progress_bar_id].total)
        self.total_progress_bar.update(1)

    def on_progress(self, progress_bar_id, count, block_size, total_size, known_size):
        self.progress_bar[progress_bar_id].update((count-self.last_progress_bar_block[progress_bar_id]) * block_size)
        self.last_progress_bar_block[progress_bar_id] = count

    def get_callbacks(self):
        return {
            "start": self.on_start,
            "progress": self.on_progress,
            "stop": self.on_stop
        }