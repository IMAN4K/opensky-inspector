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

# import plotly.express as px
import plotly.graph_objects as go
import json
import utilities

# read-only public token
MAPBOX_API_TOKEN = 'pk.eyJ1IjoiaW1hbjRrIiwiYSI6ImNsN2g0dHc5bzBiMmwzb21tMWRpcWNxZ28ifQ.qhXJV35XXhAm2l2XKkCvZg'


class Visualizer:
    def __init__(self) -> None:
        self._figure = go.Figure(go.Scattermapbox())
        self._figure.update_mapboxes(dict(
            center=go.layout.mapbox.Center(
                lat=0,
                lon=0
            ),
            zoom=3
        ))
        self._figure.update_layout(mapbox_accesstoken=MAPBOX_API_TOKEN)
        self._figure.update_layout(mapbox_style="light")
        self._figure.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        self._figure.update_layout(showlegend=False)
        self._figure.update_layout(hovermode='x')
        self._longitudes = []
        self._latitudes = []

    def loadSettings(self, descriptor):
        pass

    def addEntity(self, entity):
        position = json.loads(entity['kPosition'])['coordinates']
        track = json.loads(entity['kTrajectory'])['coordinates']

        if len(track) <= 1:
            return

        for point in track:
            self._longitudes.append(point[0])
            self._latitudes.append(point[1])

        # marker
        hoverInfo = """
        Time: {0}</br>
        Velocity: {1}</br>
        VerticalRate: {2}</br>
        CallSign: {3}</br>
        Squawk: {4}</br>
        """.format(entity['kTime'], entity['kVelocity'], entity['kVertrate'], entity['kCallsign'], entity['kSquawk'])
        bearing = utilities.calculateBearing(
            track[0][0], track[0][1], track[1][0], track[1][1])
        self._figure.add_trace(go.Scattermapbox(
            mode="markers+text",
            lon=[float("{:.6f}".format(position[0]))],
            lat=[float("{:.6f}".format(position[1]))],
            text=str(entity['kAircraftId']).upper(),
            textposition='top center',
            hovertext=hoverInfo,
            marker={'symbol': 'airport', 'size': 15, 'color': 'lightyellow', 'angle': bearing}))

        # trajectory

    def visualize(self):
        print(self._longitudes)
        print(self._latitudes)
        self._figure.add_trace(go.Scattergeo(
            mode="lines",
            lon=self._longitudes,
            lat=self._latitudes,
            line={'width': 3, 'color': 'orange'}))
        self._figure.show()
