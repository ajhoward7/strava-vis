import pandas as pd
from datetime import *
import numpy as np
import math
import plotly.graph_objs as go
import plotly


def chart_plot(by_week_activity_df):

    data = []
    custom_colours = ['blue', 'orange', 'red']
    j = 0
    for i in ['Run', 'Workout', 'Race']:
        data.append(go.Bar(
            x=by_week_activity_df['week_start'],
            y=by_week_activity_df['miles_{}'.format(i)],
            marker=dict(color=custom_colours[j]),
            name=i))
        j += 1

    layout = dict(
        barmode='stack',
        hovermode='closest',
        title='Miles per week',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(count=1,
                         label='YTD',
                         step='year',
                         stepmode='todate'),
                    dict(count=1,
                         label='1y',
                         step='year',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(),
            type='date'
        )
    )

    fig = go.Figure(data=data, layout=layout)

    return plotly.offline.plot(fig, include_plotlyjs=False,
                                 output_type='div')