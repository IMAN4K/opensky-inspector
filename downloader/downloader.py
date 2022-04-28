# MIT License

# Copyright (c) 2022 Iman Ahmadvand

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from datetime import datetime, timedelta
from multiprocessing import Pool, cpu_count
import os
import tempfile
from urllib import request, parse
import random

from numpy import double
from settings import Settings
import utilities


class Downloader:
    def __init__(self) -> None:
        self.start_date = datetime.now()
        self.end_date = datetime.now()
        self.urls = []
        self.configuration = {
            'DownloadDirectory': tempfile.gettempdir()
        }
        self.callbacks = []
        self.download_factor = 100
        self.total_download_size = 0
        self.downloaded_size = 0
        self.last_progress_hook_time = utilities.current_ms_since_epoch()

    def load_settings(self, descriptor):
        settings = Settings(descriptor, 'Download')

        configuration = settings.load()
        if len(configuration.keys()) == 0:
            settings.save(self.configuration)
        else:
            self.configuration = configuration

    def set_date_range(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def register_callback(self, callback):
        self.callbacks.append(callback)

    def set_download_factor(self, factor):
        self.download_factor = factor

    def strip(self, urls, factor):
        n = factor / 100
        return random.sample(urls, int(len(urls) * (1 - n)))

    def download_progress(self, block_num, block_size, total_size):
        if abs(self.last_progress_hook_time - utilities.current_ms_since_epoch()) > 3000:
            print('Downloading... {0:0.0f}%'.format(
                double(block_num * block_size) / self.total_download_size * 100.0))
            self.last_progress_hook_time = utilities.current_ms_since_epoch()

    def download(self, url):
        base_name = os.path.basename(parse.urlparse(url).path)
        full_name = os.path.join(
            self.configuration['DownloadDirectory'], base_name)
        try:
            path, message = request.urlretrieve(
                url, full_name, self.download_progress)
            print(path, message)
            for callback in self.callbacks:
                callback(path)
        except Exception as e:
            print(e)

    def start(self):
        self.urls.clear()
        self.total_download_size = 0
        for date in utilities.range(self.start_date.date(), self.end_date.date(), timedelta(days=1)):
            base_url = 'https://opensky-network.org/datasets/states/{}'.format(
                date)
            if utilities.UrlInformation(base_url).exists():
                day_bucket = []
                for h in utilities.range(0, 24, 1):
                    info = utilities.UrlInformation(
                        base_url + '/{0:02d}/states_{1}-{0:02d}.csv.tar'.format(h, date))
                    if info.exists():
                        day_bucket.append(info)
                for item in self.strip(day_bucket, abs(100 - self.download_factor)):
                    self.urls.append(item.get_url())
                    self.total_download_size += item.get_content_length()

        if len(self.urls) > 0:
            print('scheduling to download {0} MB for {1} samples'.format(
                self.total_download_size / 1024 / 1024, len(self.urls)))

            var = input("Willing to continue?[y|n]")
            if var == 'y' or var == 'Y':
                with Pool(cpu_count()) as pool:
                    pool.map(self.download, self.urls)
