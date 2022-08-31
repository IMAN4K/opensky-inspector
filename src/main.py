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

from cmd import Cmd
from database import Database
from downloader import Downloader
from visualizer import Visualizer
from datetime import datetime
import tarfile
import gzip
import os


class InvalidDateError(ValueError):
    pass


class DownloadCallback:
    def __init__(self, database) -> None:
        self.database = database

    def __call__(self, path):
        file = tarfile.open(path)
        file.extractall(os.path.dirname(path))
        file.close()
        os.remove(path)
        gzFilePath = str(path).replace('.tar', '.gz')
        csvFilePath = gzFilePath.replace('.gz', '')
        with gzip.open(gzFilePath) as gz:
            with open(csvFilePath, 'w+') as f:
                f.write(gz.read().decode('UTF-8'))
                f.close()
                gz.close()
                self.database.importCSV(csvFilePath)
                os.remove(csvFilePath)


class InteractiveConsole(Cmd):
    intro = 'opensky-inspector'
    prompt = intro + '> '
    workers = {
        'downloader': Downloader(),
        'database': Database(),
        'visualizer': Visualizer()
    }

    def parse(self, line):
        return str(line).split(' ')

    def do_exit(self, line):
        """
        Quitting from application
        """
        raise SystemExit()

    def do_load(self, line):
        """
        Load settings from configuration file(*.ini)
        It will be created if it doesn't exists
        e.g load ~/opensky-inspector.ini
        """
        args = self.parse(line)
        for key in self.workers:
            self.workers[key].loadSettings(args[0])

    def do_download(self, line):
        """
        Download state vector samples from https://opensky-network.org/datasets/states in given date range
        It may take some time depending on given range and network bandwith.
        download factor specifies how many samples will be downloaded per day [1%, 100%]
        format: download <start_date:[YYYY-MM-DD]> <end_date:[YYYY-MM-DD]> <download_factor:[1, 100]>
        e.g download 2020-05-11 2021-05-11 60
        """
        args = self.parse(line)
        d0 = datetime.now()
        d1 = d0
        try:
            d0 = datetime.strptime(args[0], '%Y-%m-%d')
            d1 = datetime.strptime(args[1], '%Y-%m-%d')
        except Exception as e:
            raise InvalidDateError(
                "Incorrect date format!(should be YYYY-MM-DD)")

        if d0 > d1:
            raise ValueError('Invalid date sequence!')

        factor = int(args[2])

        if not 1 <= factor <= 100:
            raise ValueError('Invalid download factor!')

        downloader = self.workers['downloader']
        downloader.callbacks = [DownloadCallback(self.workers['database'])]
        downloader.startDate = d0
        downloader.endDate = d1
        downloader.downloadFactor = factor
        downloader.start()

    def do_import(self, line):
        """
        Import & normalize state vector samples into database
        it may take some time depending on system setup and database configuration
        """
        self.workers['database'].start()

    def do_visualize(self, args):
        """
        Visualize the active flights at given time point from imported state vector samples
        """
        visualizer = self.workers['visualizer']
        tuples = self.workers['database'].query(1591021770)
        for tuple in tuples:
            visualizer.addEntity(tuple)
        visualizer.visualize()


if __name__ == "__main__":
    console = InteractiveConsole()
    console.cmdloop('Enter a command to proceed...')
