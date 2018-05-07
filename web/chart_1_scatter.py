import pandas as pd
from datetime import *
import numpy as np
import math
import plotly.graph_objs as go
import plotly


def chart_plot(activities_df):

    sizeref = 20 * max(activities_df['size']) / (100 ** 2)
    data = []
    for run_type in ['Run', 'Workout', 'Long Run', 'Race']:
        trace = go.Scatter(
            x=activities_df['miles'][activities_df['workout_type'] == run_type],
            y=activities_df['pace_mile'][activities_df['workout_type'] == run_type],
            mode='markers',
            hoverinfo='text',
            opacity=0.8,
            name=run_type,
            hovertext=activities_df['text'][activities_df['workout_type'] == run_type],
            marker=dict(
                symbol='circle',
                sizemode='area',
                sizeref=sizeref,
                size=activities_df['size'][activities_df['workout_type'] == run_type],
                line=dict(
                    width=2
                ),
            )
        )
        data.append(trace)

    layout = go.Layout(
        title='Run Summary',
        hovermode='closest',
        xaxis=dict(
            title='Distance (Miles)',
            gridcolor='rgb(255, 255, 255)',
            range=[0, 20],
            zerolinewidth=1,
            ticklen=5,
            gridwidth=2,
        ),
        yaxis=dict(
            title='Pace (Seconds per Mile)',
            gridcolor='rgb(255, 255, 255)',
            range=[0, 600],
            zerolinewidth=1,
            ticklen=5,
            gridwidth=2,
        ),
        paper_bgcolor='rgb(243, 243, 243)',
        plot_bgcolor='rgb(243, 243, 243)',
    )

    fig = go.Figure(data=data, layout=layout)

    #return plotly.offline.plot(fig, include_plotlyjs=False,
     #                            output_type='div')
    return fig