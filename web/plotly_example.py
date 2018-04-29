import plotly
from plotly.graph_objs import Data, Layout, Marker, Scattermapbox


def plotly_map():
    mapbox_access_token = 'pk.eyJ1Ijoic3VodHdpbnMiLCJhIjoi' +\
                        'Y2pnNGJvbXRhMGpoNDJwcWRva3JieWgwcCJ9' +\
                        '.cmsuwG65XkGUh2pv07nIVg'

    data = Data([
        Scattermapbox(
            lat=['37.7765', '37.791377'],
            lon=['-122.4506', '-122.392609'],
            mode='markers',
            marker=Marker(size=15),
            text=["University of San Francisco, Main Campus",
                  "University of San Francisco, Downtown Campus"])])
    layout = Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=37.773972,
                lon=-122.431297
            ),
            pitch=0,
            zoom=11
        ),
    )

    fig = dict(data=data, layout=layout)
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

    by_week_activity_df = by_week_activity_df[['week_start', 'miles', 'miles_Workout', 'miles_Long Run', 'miles_Race']]
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
