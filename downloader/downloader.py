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
from time import sleep
from urllib import request, parse
from settings import Settings
import utilities


class Downloader:
    def __init__(self) -> None:
        self.start_date = datetime.now()
        self.end_date = datetime.now()
        self.finish_callbacks = []
        self.urls = []
        self.configuration = {
            'DownloadDirectory': tempfile.gettempdir()
        }

    def load_settings(self, descriptor):
        settings = Settings(descriptor, 'Download')

        if len(settings.load().keys()) == 0:
            settings.save(self.configuration)
        else:
            self.configuration = settings.load()

    def register_finish_callbacks(self, callback):
        self.finish_callbacks.append(callback)

    def set_date_range(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def download1(self, url):
        print('Downloading... {0}'.format(url))
        sleep(1)
        # base_name = os.path.basename(parse.urlparse(url).path)
        # full_name = os.path.join(self.configuration['DownloadDirectory'], base_name)
        # path, message = request.urlretrieve(url, full_name)
        # try:
        #     path, message = request.urlretrieve(url, full_name)
        #     print(path, message)
        #     for item in self.finish_callbacks:
        #         item(path)
        # except Exception as e:
        #     print(e)

    def test(self, url):
        pass

    def start(self):
        self.urls.clear()
        total_download_size = 0
        for date in utilities.range(self.start_date.date(), self.end_date.date(), timedelta(days=1)):
            base_url = 'https://opensky-network.org/datasets/states/{}'.format(
                date)
            if utilities.UrlInformation(base_url).exists():
                for h in utilities.range(0, 24, 1):
                    info = utilities.UrlInformation(
                        base_url + '/{0:02d}/states_{1}-{0:02d}.csv.tar'.format(h, date))
                    if info.exists():
                        self.urls.append(info.get_url())
                        total_download_size += info.get_content_length()

        if len(self.urls) > 0:
            print('scheduling to download {0} MB for {1} samples'.format(
                total_download_size / 1024 / 1024, len(self.urls)))

            var = input("Willing to continue?[y|n]")
            if var == 'y' or var == 'Y':
                with Pool(1) as pool:
                    pool.map(self.test, self.urls)


object = Downloader()
object.load_settings('/home/iman/opensky.ini')
object.set_date_range(datetime.date(2020, 5, 25), datetime.date(2020, 5, 25))
