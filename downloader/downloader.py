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
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool as Pool
import os
import tempfile
from urllib import request, parse
from settings import Settings
import utilities


class DownloadProgress:
    def __init__(self, url, updateInterval, callback) -> None:
        self._url = url
        self._updateInterval = updateInterval
        self._callback = callback

        self._lastHookTime = utilities.currentMsSinceEpoch()

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, arg):
        self._url = arg

    @property
    def updateInterval(self):
        return self._updateInterval

    @updateInterval.setter
    def updateInterval(self, arg):
        self._updateInterval = arg

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, arg):
        self._callback = arg

    def __call__(self, block_num, block_size, total_size):
        if abs(self._lastHookTime - utilities.currentMsSinceEpoch()) > self.updateInterval:
            self.callback(self.url, float(block_num * block_size))
            self._lastHookTime = utilities.currentMsSinceEpoch()


class Downloader:
    def __init__(self) -> None:
        self._startDate = datetime.now()
        self._endDate = self._startDate
        self._callbacks = []
        self._downloadFactor = 100

        self._urls = []
        self._configuration = {
            "downloaddirectory": tempfile.gettempdir()
        }
        self._totalDownloadSize = 0
        self._progress = {}

    @property
    def startDate(self):
        return self._startDate

    @startDate.setter
    def startDate(self, arg):
        self._startDate = arg

    @property
    def endDate(self):
        return self._endDate

    @endDate.setter
    def endDate(self, arg):
        self._endDate = arg

    @property
    def callbacks(self):
        return self._callbacks

    @callbacks.setter
    def callbacks(self, arg):
        self._callbacks = arg

    @property
    def downloadFactor(self):
        return self._downloadFactor

    @downloadFactor.setter
    def downloadFactor(self, arg):
        self._downloadFactor = arg

    def loadSettings(self, descriptor):
        settings = Settings(descriptor, 'Download')

        configuration = settings.load()
        if len(configuration.keys()) == 0:
            settings.save(self._configuration)
        else:
            self._configuration = configuration

    def progress(self, url, total):
        self._progress[url] = total
        print('Downloading... {0:0.0f}%'.format(
            sum(self._progress.values()) / self._totalDownloadSize * 100.0))

    def download(self, url):
        base_name = os.path.basename(parse.urlparse(url).path)
        full_name = os.path.join(
            self._configuration["downloaddirectory"], base_name)
        try:
            path, message = request.urlretrieve(
                url, full_name, DownloadProgress(url, 3000, self.progress))
            for callback in self._callbacks:
                callback(path)
        except Exception as e:
            print(e)

    def start(self):
        self._urls.clear()
        self._progress.clear()
        self._totalDownloadSize = 0

        for date in utilities.range(self.startDate.date(), self.endDate.date(), timedelta(days=1)):
            base_url = 'https://opensky-network.org/datasets/states/{}'.format(
                date)
            if utilities.UrlInformation(base_url).exists():
                day_bucket = []
                for h in utilities.range(0, 24, 1):
                    info = utilities.UrlInformation(
                        base_url + '/{0:02d}/states_{1}-{0:02d}.csv.tar'.format(h, date))
                    if info.exists():
                        day_bucket.append(info)
                for item in utilities.strip(day_bucket, abs(100 - self.downloadFactor)):
                    print(item.url)
                    self._urls.append(item.url)
                    self._totalDownloadSize += item.contentLength()

        if len(self._urls) > 0:
            print('scheduling to download {0} MB for {1} samples'.format(
                self._totalDownloadSize / 1024 / 1024, len(self._urls)))

            var = input("Willing to continue?[y|n]")
            if var == 'y' or var == 'Y':
                with Pool(cpu_count()) as pool:
                    pool.map(self.download, self._urls)
