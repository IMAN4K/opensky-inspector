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
from settings import Settings


class InvalidDateError(ValueError):
    pass


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
        Load settings from configuration file(.ini)
        It will be created if doesn't exists
        e.g load ~/opensky-inspector.ini
        """
        args = self.parse(line)
        for key in self.workers:
            self.workers[key].load_settings(args[0])

    def do_download(self, line):
        """
        Download state vector samples from https://opensky-network.org in given date range
        It may take some time depending on given range and network bandwith
        e.g download 2020-05-11 2021-05-11
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
        self.workers['downloader'].set_date_range(d0, d1)
        self.workers['downloader'].start()

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
        pass


if __name__ == "__main__":
    set = Settings('/home/iman/opensky.ini')
    set.save({'Im@n': 'Ahmadvand'})
    # console = InteractiveConsole()
    # console.cmdloop('Enter a command to proceed...')
