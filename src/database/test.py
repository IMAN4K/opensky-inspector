import plotly.express as px
import plotly.graph_objects as go

fig = go.Figure(go.Scattermapbox())

fig.update_mapboxes(dict(
                    center=go.layout.mapbox.Center(
                        lat=0,
                        lon=0
                    ),
                    zoom=3
                    ))
fig.update_layout(
    mapbox_accesstoken='pk.eyJ1IjoiaW1hbjRrIiwiYSI6ImNsN2g0dHc5bzBiMmwzb21tMWRpcWNxZ28ifQ.qhXJV35XXhAm2l2XKkCvZg')
fig.update_layout(mapbox_style="light")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.update_layout(showlegend=False)

# track
fig.add_trace(go.Scattermapbox(
    mode="lines",
    lon=[-50, -60, 40],
    lat=[30, 10, -20],
    line={'width': 2, 'color': 'yellow'}))

# image
fig.add_trace(go.Scattermapbox(
    mode="markers+text",
    lon=[-50],
    lat=[30],
    text='65FA332',
    textposition='top center',
    hovertext='Item: ITEM</br>ITEM:ITEM',
    marker={'symbol': 'airport', 'size': 15,
            'color': 'lightyellow', 'angle': 95.0}),)

fig.show()
