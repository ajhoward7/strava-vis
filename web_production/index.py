import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import Flask, render_template

from apps import alex_dashboard, personalised_dashboard


server = Flask(__name__)

app = dash.Dash(__name__, server=server, url_base_pathname='/dash')

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@server.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/app1':
         return "helllooo"
    elif pathname == '/apps/app2':
         return "Here is app 2"
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)