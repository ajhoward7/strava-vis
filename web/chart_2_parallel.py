import pandas as pd
from datetime import *
import numpy as np
import math
import plotly.graph_objs as go
import plotly


days_dict = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}


def chart_plot(by_week_df):
    dimensions = []
    for i in range(7):
        dimensions.append(
            dict(range=[0, 20],
                 constraintrange=[0, 20],
                 label='{}'.format(days_dict[i]), values=by_week_df['miles_{}'.format(i)]))

    data = [
        go.Parcoords(
            line=dict(color=by_week_df['miles'],
                      colorscale='Hot',
                      showscale=True,
                      reversescale=True),
            opacity=0.5,
            dimensions=dimensions, hoverinfo='text')

    ]

    layout = go.Layout(
        plot_bgcolor='#E5E5E5',
        paper_bgcolor='#E5E5E5',
        title='Miles per week broken down by day'
    )

    fig = go.Figure(data=data, layout=layout)

    return plotly.offline.plot(fig, include_plotlyjs=False,
                                 output_type='div')