import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from flask import Flask, redirect, render_template, url_for, flash, request
from flask_bootstrap import Bootstrap
from plotly_plotting import plot_charts, preprocess_activities
from scrape import scrape_activities
from credentials import client_id, client_secret
import requests
import json
from datetime import *
import polyline

#mapbox_access_token = "pk.eyJ1IjoiYWxleGhvd2FyZDk1IiwiYSI6ImNqZ29rcHV1czA4YTEzM3I0cmNkd3NkcjAifQ.NnlWZRHbvLxAFXV6sLh3rg"
mapbox_access_token = 'pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w'

server = Flask(__name__)

@server.route('/', methods=['GET', 'POST'])
def login():
    url = 'https://www.strava.com/oauth/authorize?response_type=code&redirect_uri=http%3A%2F%2F54.214.153.34%2Fauthorize&client_id=20812'
    return '<a href={}>Click here to authorise</a>'.format(url)


@server.route('/authorize', methods=('GET','POST'))
def home():
    code = request.args.get('code')
    r = requests.post('https://www.strava.com/oauth/token', data={'client_id':client_id, 'client_secret':client_secret, 'code':code})
    json_data = json.loads(r._content)
    access_token = json_data["access_token"]
    username = scrape_activities(access_token)

    return redirect('/{}'.format(username))


activities_df = preprocess_activities('alex')

days_dict = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}

activities_grouped_df = activities_df.groupby(['date'], as_index=False)['miles'].sum()
activities_grouped_df['dow'] = activities_grouped_df.date.apply(lambda x: x.weekday())
activities_grouped_df['week_start'] = activities_grouped_df.date.apply(lambda x: x - timedelta(days=x.weekday()))

miles_per_week = activities_grouped_df.groupby(['week_start'], as_index=False).miles.sum()
by_week_df = pd.DataFrame(activities_grouped_df.week_start.unique(), columns=['week_start'])
by_week_df['miles'] = 0

for i in range(7):
    by_week_df['{}'.format(i)] = i

for i in range(7):
    by_week_df = pd.merge(by_week_df, activities_grouped_df, left_on=['week_start', '{}'.format(i)],
                          right_on=['week_start', 'dow'], how='left', suffixes=('', '_{}'.format(i)))

by_week_df = by_week_df[['week_start', 'miles_0', 'miles_1', 'miles_2', 'miles_3', 'miles_4', 'miles_5', 'miles_6']]
by_week_df['year'] = by_week_df['week_start'].apply(lambda x: x.year)
by_week_df.fillna(0, inplace=True)
by_week_df = pd.merge(by_week_df, miles_per_week, how='left', on='week_start')


app = dash.Dash(server=server, url_base_pathname='/dash')

app.layout = html.Div([
    html.Div([
        html.H2("Strava-Vis")
    ], className='banner'),

    html.Div(dcc.Slider(
        id='crossfilter-year--slider',
        min=activities_df['year'].min(),
        max=activities_df['year'].max(),
        value=activities_df['year'].max(),
        step=None,
        marks={str(year): str(year) for year in activities_df['year'].unique()}
    ), style={'width': '45%', 'padding': '0px 30px 30px 30px'}),

    html.Div(
        className="row",
        children=[
            html.Div(
                className="six columns",
                children=[
                    html.Div(
                        children=dcc.Graph(
                            id='crossfilter-indicator-scatter',
                            hoverData={'points': [{'customdata': list(activities_df.id)[0]}]}
                        )
                    ),
                    html.Div(className='row',
                             children = [
                                            html.Div(
                                            className="six columns",
                                            children=[dcc.Graph(id='miles-hist')]),
                                            html.Div(className="six columns",
                                            children=[dcc.Graph(id='weekly-mileage')])]



                    )
                ]
            ),
            html.Div(
                className="six columns",
                children=html.Div([
                    dcc.Graph(
                        id='parallel'
                    ),
                    dcc.Graph(
                        id='run-geo'
                    ),
                    dcc.Graph(id='weekly-mileage')

                ])
            )
        ]
    )
])

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('crossfilter-year--slider', 'value')])
def update_graph(year_value):
    df2 = activities_df[activities_df['year'] == year_value]

    sizeref = 20 * max(activities_df['size']) / (100 ** 2)
    data = []
    for run_type in ['Run', 'Workout', 'Long Run', 'Race']:
        trace = go.Scatter(
            x=df2['miles'][df2['workout_type'] == run_type],
            y=df2['pace_mile'][df2['workout_type'] == run_type],
            mode='markers',
            hoverinfo='text',
            opacity=0.8,
            name=run_type,
            customdata=df2['id'][df2['workout_type']==run_type],
            hovertext=df2['text'][df2['workout_type'] == run_type],
            marker=dict(
                symbol='circle',
                sizemode='area',
                sizeref=sizeref,
                size=df2['size'][df2['workout_type'] == run_type],
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
        autosize=False
    )

    return {'data':data, 'layout':layout}


def create_time_series(this_week, title):
    days_dict = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    this_week = this_week.sort_values(['day'], ascending = True)
    this_week.day = this_week.day.apply(lambda x : days_dict[x])
    custom_colours = {'Run': 'blue', 'Workout':'orange', 'Race':'red', 'Long Run':'green'}

    data = []
    for day in days_dict.values():
        data.append(go.Bar(
            orientation = 'h',
            y=[day],
            x=[0],
            marker=dict(opacity=[0])))

    for index, row in this_week.iterrows():
        data.append(go.Bar(
            orientation = 'h',
            y=[row['day']],
            x=[row['miles']],
            marker=dict(color=[custom_colours[row['workout_type']]],
                        opacity = [0.75]),
            hovertext=[row['text']],
            hoverinfo = 'text'))



    layout = dict(
        hovermode='closest',
        barmode='stack',
        title=title,
        autosize=False,
        showlegend=False
        )

    return {'data': data, 'layout':layout}


@app.callback(
    dash.dependencies.Output('weekly-mileage', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData')])

def update_mileage(hoverData):
    id = hoverData['points'][0]['customdata']
    activity = activities_df[activities_df.id == id]
    date = list(pd.to_datetime(activity.date))[0]
    week_start = date - timedelta(days=date.weekday())
    week_end = week_start + timedelta(days=6)
    this_week = activities_df[activities_df.week_start == week_start]

    this_week['day'] = this_week.date.apply(lambda x: x.weekday())
    total_miles = this_week.miles.sum()
    title = '<b>{} - {}</b><br>Total Miles: {}'.format(week_start.date(), week_end.date(), int(total_miles))

    return create_time_series(this_week, title)


def create_geo(summary_polyline):
    gps = polyline.decode(summary_polyline)
    df = pd.DataFrame(gps, columns=['lat', 'long'])
    df['cnt'] = 1

    data = go.Data([
        go.Scattermapbox(
            lat=df.lat,
            lon=df.long,
            mode='lines',
            marker=go.Marker(
                size=17,
                color='rgb(255, 0, 0)',
                opacity=0.7
            )
        )])

    layout = go.Layout(
        autosize=False,
        hovermode='closest',
        showlegend=False,
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=df.lat[int(len(df)/4)],
                lon=df.long[int(len(df)/4)]
            ),
            pitch=0,
            zoom=10.5,
            style='light'
        ),
    )

    fig = dict(data=data, layout=layout)

    return fig


@app.callback(
    dash.dependencies.Output('run-geo', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData')])
def update_geo(hoverData):
    id = hoverData['points'][0]['customdata']
    summary_polyline = list(activities_df[activities_df.id==id]['map.summary_polyline'])[0]

    return create_geo(summary_polyline)


def create_parallel(by_week_df_2):
    dimensions = []
    for i in range(7):
        dimensions.append(
            dict(range=[0, 20],
                 label='{}'.format(days_dict[i]), values=by_week_df_2['miles_{}'.format(i)]))

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

    return go.Figure(data=data, layout=layout)



@app.callback(
    dash.dependencies.Output('parallel', 'figure'),
    [dash.dependencies.Input('crossfilter-year--slider', 'value')])
def update_parallel(year_value):
    by_week_df_2 = by_week_df[by_week_df.year==year_value]

    return create_parallel(by_week_df_2)


def create_distance_hist(all_miles, this_miles):
    trace1 = go.Histogram(

        x=all_miles[(all_miles >= this_miles-0.5)&(all_miles < this_miles + 0.5)],
        hoverinfo='text'
    )
    trace0 = go.Histogram(
        x=all_miles[(all_miles < this_miles-0.5)|(all_miles >= this_miles + 0.5)],
        hoverinfo='text'
    )
    data = [trace0, trace1]
    layout = go.Layout(barmode='stack',
                       showlegend=False,
                       bargap=0.2)
    return go.Figure(data=data, layout=layout)


@app.callback(
    dash.dependencies.Output('miles-hist', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData')])
def update_distance_hist(hoverData):
    id = hoverData['points'][0]['customdata']
    activity = activities_df[activities_df.id == id]
    year = list(activity.year)[0]
    all_miles = activities_df[activities_df.year==year]['miles'].apply(lambda x : round(x))
    this_miles = int(list(activity['miles'])[0])

    return create_distance_hist(all_miles, this_miles)



if __name__ == '__main__':
    app.run_server(debug=True)