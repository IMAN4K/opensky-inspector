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

from configparser import ConfigParser


class Settings():
    def __init__(self, descriptor, group='General') -> None:
        self._parser = ConfigParser()  # use INI parser as backend
        self._descriptor = descriptor
        self._group = group

    def save(self, dict):
        self._parser.read(self._descriptor)

        try:
            self._parser.add_section(self._group)
        except Exception:  # DuplicateSectionError
            pass

        for k in dict:
            self._parser.set(self._group, k, dict[k])

        with open(self._descriptor, 'w') as file:
            self._parser.write(file)
            file.close()

    def load(self):
        result = {}
        self._parser.read(self._descriptor)
        options = []
        try:
            options = self._parser.options(self._group)
        except Exception:
            pass
        for option in options:
            try:
                value = self._parser.get(self._group, option)
                if value != -1:
                    result[option] = value
            except Exception:
                pass
        return result
