import pandas as pd
from datetime import *
import numpy as np
import math
import plotly.plotly  as py
import plotly.graph_objs as go
import json
import plotly

metres_mile = 1609.34
workout_type_dict = {0:'Run',1:'Race',2:'Long Run',3:'Workout'}


def process_activities(username):
    activities_df = pd.read_json('{}/activities.json'.format(username))

    activities_df = activities_df[
        ['average_speed', 'distance', 'moving_time', 'name', 'start_date_local', 'id', 'workout_type', 'type']]
    activities_df = activities_df[activities_df.type == 'Run']

    activities_df['pace_mile'] = metres_mile / activities_df.average_speed
    activities_df['pace_km'] = 1000 / activities_df.average_speed

    activities_df['date'] = pd.to_datetime(activities_df.start_date_local.apply(lambda x: x.split('T')[0]))
    activities_df.drop(['average_speed', 'start_date_local', 'type', 'id'], axis=1, inplace=True)

    activities_df.workout_type = activities_df.workout_type.fillna(0)
    activities_df.workout_type = activities_df.workout_type.apply(lambda x: workout_type_dict[x])

    activities_df['miles'] = activities_df.distance / metres_mile
    activities_df['Distance (Kilometres)'] = activities_df.distance / 1000

    activities_df['size'] = activities_df.moving_time.astype('float').apply(lambda x: math.sqrt(x))
    sizeref = 20 * max(activities_df['size']) / (100 ** 2)
    activities_df['year'] = activities_df.date.apply(lambda x: x.year)

    activities_text = []
    for i in range(len(activities_df)):
        row = activities_df.iloc[i,]
        activities_text.append('{}<br>{}<br>'.format(row['name'].encode('ascii', 'ignore'),
                                                     row['date'].date()) + '{:.1f} miles<br>{:.2f} seconds/mile'.format(
            row['miles'], row['pace_mile']))

    activities_df['text'] = activities_text

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

    output = plotly.offline.plot(fig, include_plotlyjs=False,
                                 output_type='div')

    return output
