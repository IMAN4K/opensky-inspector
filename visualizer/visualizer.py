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

import folium
import webbrowser
import tempfile
import os


class Visualizer:
    def __init__(self) -> None:
        self._map = folium.Map(
            location=[0, 0], zoom_start=4, tiles="Stamen Terrain")

    def loadSettings(self, descriptor):
        pass

    def addEntity(self, entity):
        print(entity)
        loc = [(54.32, 32.54), (40.721, -73.996)]

        folium.PolyLine(loc,
                        color='yellow',
                        weight=3,
                        opacity=0.8).add_to(self._map)

        folium.Marker(
            location=[54.32, 32.54],
            popup='Aircraft',
            icon=folium.DivIcon(
                html=f"""<div><p>This is some text </br>in a div element.</p></div> <div style="
                background: url(/home/iman/prj/UAV/uav-3d/plugins/uav-unit/res/symbols/airplane.png) no-repeat;
                width: 128px;
                height: 128px;
                display:inline-block;
                transform: rotate(80deg);
                border: none;"></div>""", icon_size=(128, 128))
        ).add_to(self._map)

    def clear(self):
        out = os.path.join(tempfile.gettempdir(), 'map.html')
        if os.path.exists(out):
            os.remove(out)

    def visualize(self):
        out = os.path.join(tempfile.gettempdir(), 'map.html')
        self._map.save(out)
        webbrowser.open(out)
