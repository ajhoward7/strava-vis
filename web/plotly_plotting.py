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

    activities_grouped_df = activities_df.groupby(['date'], as_index=False)['miles'].sum()
    activities_grouped_df['dow'] = activities_grouped_df.date.apply(lambda x: x.weekday())
    activities_grouped_df['week_start'] = activities_grouped_df.date.apply(lambda x: x - timedelta(days=x.weekday()))

    miles_per_week = activities_grouped_df.groupby(['week_start'], as_index=False).miles.sum()
    by_week_df = pd.DataFrame(activities_grouped_df.week_start.unique(), columns=['week_start'])

    for i in range(7):
        by_week_df['{}'.format(i)] = i

    for i in range(7):
        by_week_df = pd.merge(by_week_df, activities_grouped_df, left_on=['week_start', '{}'.format(i)],
                              right_on=['week_start', 'dow'], how='left', suffixes=('', '_{}'.format(i)))

    by_week_df = by_week_df[['week_start', 'miles', 'miles_1', 'miles_2', 'miles_3', 'miles_4', 'miles_5', 'miles_6']]
    by_week_df.columns = ['week_start', 'miles_0', 'miles_1', 'miles_2', 'miles_3', 'miles_4', 'miles_5', 'miles_6']
    by_week_df['year'] = by_week_df['week_start'].apply(lambda x: x.year)
    by_week_df.fillna(0, inplace=True)
    by_week_df = pd.merge(by_week_df, miles_per_week, how='left', on='week_start')

    days_dict = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}

    dimensions = list()

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

    output2 = plotly.offline.plot(fig, include_plotlyjs=False,
                                 output_type='div')

    activities_df['week_start'] = activities_df.date.apply(lambda x: x - timedelta(days=x.weekday()))
    activities_grouped_df_2 = activities_df.groupby(['workout_type', 'week_start'], as_index=False)['miles'].sum()

    by_week_activity_df = pd.DataFrame(activities_grouped_df_2.week_start.unique(), columns=['week_start'])

    for i in activities_df.workout_type.unique():
        by_week_activity_df['{}'.format(i)] = i

    for i in range(4):
        by_week_activity_df = pd.merge(by_week_activity_df, activities_grouped_df_2,
                                       left_on=['week_start', '{}'.format(activities_df.workout_type.unique()[i])],
                                       right_on=['week_start', 'workout_type'], how='left',
                                       suffixes=('', '_{}'.format(activities_df.workout_type.unique()[i])))

    if 'miles_Long Run' not in by_week_activity_df.columns:
        by_week_activity_df['miles_Long Run'] = 0

    by_week_activity_df = by_week_activity_df[['week_start', 'miles_Run', 'miles_Workout', 'miles_Long Run', 'miles_Race']]
    by_week_activity_df.columns = ['week_start', 'miles_Run', 'miles_Workout', 'miles_Long Run', 'miles_Race']
    by_week_activity_df.fillna(0, inplace=True)

    by_week_activity_df['miles_Run'] = np.array(by_week_activity_df['miles_Run']) + np.array(
        by_week_activity_df['miles_Long Run'])

    by_week_activity_df['miles_Run'] = np.array(by_week_activity_df['miles_Run']) + np.array(
        by_week_activity_df['miles_Long Run'])

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

    output3 = plotly.offline.plot(fig, include_plotlyjs=False,
                                 output_type='div')

    return(output,output2,output3)

