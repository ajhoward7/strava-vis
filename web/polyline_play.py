import polyline
import pandas as pd
import plotly
from plotly.graph_objs import *

mapbox_access_token = "pk.eyJ1IjoiYWxleGhvd2FyZDk1IiwiYSI6ImNqZ29rcHV1czA4YTEzM3I0cmNkd3NkcjAifQ.NnlWZRHbvLxAFXV6sLh3rg"

gps = polyline.decode("{jqeFr{jjV`BpVvJ[CvHhGdLtBrWxEdHmCnQu@pWtBbK}CbDjA~Fl@ne@~DvLwCzR^n_@nAtLF`UfChG{@|OjBdCtHO~AcBUeJaBmNuGiSc@_HX_W`DoKGoS_Is`@jEsYoIkQi@kR}@_AdDkT{E_HsBqWuFuLo@mHoI@_AsV")

df = pd.DataFrame(gps, columns = ['lat','long'])
df['cnt']=1

data = Data([
    Scattermapbox(
        lat=df.lat,
        lon=df.long,
        mode='lines',
        marker=Marker(
            size=17,
            color='rgb(255, 0, 0)',
            opacity=0.7
        )
    )])

layout = Layout(
    autosize=True,
    hovermode='closest',
    showlegend=False,
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(
            lat=df.lat[0],
            lon=df.long[0]
        ),
        pitch=0,
        zoom=12,
        style='light'
    ),
)

fig = dict( data=data, layout=layout )
plotly.offline.plot(fig)