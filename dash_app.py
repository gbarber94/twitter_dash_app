"""
Twitter_stats: dash app
July 16, 2019
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
#import dash_table
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
#from io import BytesIO
import base64
#import numpy as np
import data_retreival


# Load in Data , change to load from source

tweets = pd.read_csv('twitter.csv', encoding = "ISO-8859-1")
# Data pre processing
tweets['message'] = tweets['message'].astype(str)
tweets['message'] = tweets['message'].map(lambda x: x[:-2])
tweets['message'] = tweets['message'].map(lambda x: x.replace('\\n','<br>'))

# Data for heatmap
tweets_hm = tweets
tweets_hm['created_at'] = pd.to_datetime(tweets_hm['created_at'], utc = True)
tweets_hm['datetime'] = pd.to_datetime(tweets_hm['created_at'].dt.date)
tweets_hm['sum'] = 1

#selection choices
year_vals = list(tweets_hm['created_at'].dt.year.unique()) #list of years covered
author_vals = list(tweets_hm['author_name'].unique()) #list of authors


# App Starts Here:

#default
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#bootstrap style sheet
external_stylesheets = ['https://codepen.io/amyoshino/pen/jzXypZ.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = 'Twitter_stats'


"""
==========================================================================================
ui Section:
==========================================================================================
"""

app.layout = (
    html.Div([
        dcc.Tabs(id="tabs", children=[

            # Tab 1: Overall

            dcc.Tab(label='Overall', children=[
                html.Div([
                    html.H1(children='Twitter_stats Overall'),

                    html.Div(children='''
                        Select a Year:
                    '''),

                ]),
                html.P(id='placeholder') ,
                html.Div([
                    html.Div([
                        dcc.Dropdown(
                            id = "year2",
                            options = [{'label': i, 'value': i} for i in year_vals],
                            placeholder = "Select a Year",
                            value = 2019),
                        dcc.Graph(id='table2',config={'displayModeBar': False})
                       # html.Div(id='table'),
                    ],className='four columns'

                    ),

                    html.Div([dcc.Graph(id='Heatmap2',config={'displayModeBar': False},style={'padding-bottom' : 0}),
                             html.Img(id = 'Image2',style={
                    'height' : '50%',
                    'width' : '60%',
                    'float' : 'center',
                    'position' : 'center',
                    'padding-top' : 0,
                    'padding-right' : 0,
                    'padding-left' : 200

                }),],
                            className='eight columns')
                ],className="row"
                ),
            ]),

            # Tab two: By Account

            dcc.Tab(label='By Account', children=[
                html.Div([
                    html.H1(children='Twitter_stats by Account'),

                    html.Div(children='''
                        Select a Account:
                    '''),

                ]),
                html.Div([
                    html.Div([
                        dcc.Dropdown(
                            id = "author",
                            options =[{'label': i, 'value': i} for i in author_vals],
                            placeholder = "Select an Author"),
                        dcc.Dropdown(
                            id = "year",
                            options = [{'label': i, 'value': i} for i in year_vals],
                            placeholder = "Select a Year",
                            value = 2019),
                        dcc.Graph(id='table',config={'displayModeBar': False})
                       # html.Div(id='table'),
                    ],className='four columns'

                    ),

                    html.Div([dcc.Graph(id='Heatmap',config={'displayModeBar': False},style={'padding-bottom' : 0}),
                             html.Img(id = 'Image',style={
                    'height' : '50%',
                    'width' : '60%',
                    'float' : 'center',
                    'position' : 'center',
                    'padding-top' : 0,
                    'padding-right' : 0,
                    'padding-left' : 200

                }),],
                            className='eight columns')


                ],className="row"
                ),
                 ]),
                dcc.Tab(label='Update', children=[
                    dcc.Markdown('''
                        Check to update:
                        note will take ~ 10 mins to update
                    '''),

                    dcc.Checklist(id = 'check',
                    options=[
                    {'label': 'Update', 'value': 'up'}
                    ]
                    ),])



    ])
 ])
)

"""
==========================================================================================
Server Section:
==========================================================================================
"""

# Reload data

@app.callback(
	Output('placeholder','children'),
	[Input('check','value')])

def csv_up(check):
    print(check)
    if check == ['up']:
        print('restart')
        data_retreival.data_pull()

    else:
        print('no')


# Tab 1: Overall

# Heat map

@app.callback(
	Output('Heatmap2','figure'),
	[Input('year2','value')])

def plot_heatmap2(year_v):
    tweets_hm1 = tweets_hm[tweets_hm['created_at'].dt.year == year_v][['datetime','sum',]]
    tweets_hm1 = tweets_hm1[['datetime','sum']].set_index('datetime')
    tweets_hm1.index = pd.DatetimeIndex(tweets_hm1.index)
    tweets_hm1 = tweets_hm1.resample('D').sum().reset_index()
    tweets_hm1['datetime'] = pd.to_datetime(tweets_hm1['datetime'], utc = True)
    tweets_hm1['weekday'] = tweets_hm1['datetime'].dt.weekday
    tweets_hm1['weeknumber'] = tweets_hm1['datetime'].dt.week

    #Format hover text
    text = ['Tweet Count: {} <br>Date: {} '.format(str(j),str(i)) for i, j in zip(tweets_hm1['datetime'].dt.date, tweets_hm1['sum'])]

    data = [
        go.Heatmap(
            y = tweets_hm1['weekday'],
            x = tweets_hm1['weeknumber'],
            z = tweets_hm1['sum'],
            text= text,
            hoverinfo='text',
            xgap=3,
            ygap=3,
            showscale=False,
            colorscale= 'reds'
        )
    ]

    layout = (
        go.Layout(
            title='Tweet Frequency: {} '.format(year_v),
            height=300,
            yaxis=dict(ticks = '',
            showline = False, showgrid = False, zeroline = False,
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            tickvals=[0,1,2,3,4,5,6],
            ),
            xaxis=dict(ticks = '',
            showline = False, showgrid = False, zeroline = False,
            ticktext=[ 'Mon','January', 'Febuary', 'March', 'April', 'May',
            'June','July','August','September','October','November','December'],
            tickvals=[0,4,8,12,16,20,24,28,32,36,40,44,48,52],
            ),
            margin = dict(t=45,pad = 0),
        )
    )

    fig = go.Figure(data=data, layout=layout)
    fig.update_yaxes(autorange="reversed")
    return fig

# Plotly Tweet Tabel

@app.callback(
    Output('table2', 'figure'),
    [Input('year2','value')])

def update_table(year_v):
    tweets_hm2 = tweets_hm[tweets_hm['created_at'].dt.year == year_v][['created_at','author_name','message']]
    df = tweets_hm2.sort_values(by='created_at',ascending=False)
    fig1 = go.Figure(data=[go.Table(
    header=dict(values=list(df.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[df.created_at,df.author_name,df.message],
               fill_color='lavender',
               align='left',
              ))
],
    layout = (
        go.Layout(title = '<b>tweets',
                  height=500,
                  margin = dict(t=55,b=0,r=0,l=0)
                  )))

    return fig1

# Tweet word map

@app.callback(
    Output('Image2', 'src'),
    [Input('year2','value')])

def word_c2(year_v):
    text = tweets[['message','created_at']]
    text['created_at'] = pd.to_datetime(text['created_at'],utc=True)
    text = text[text['created_at'].dt.year == year_v]['message']
    wordcloud = WordCloud(
    width = 1000,
    height = 450,
    background_color = 'white',
    stopwords = STOPWORDS.update(['u00e7','u00f5es','u00e7o'])).generate(str(text))
    wordcloud.to_file('wc_overall.png')
    test_png = 'wc_overall.png'
    test_base64 = base64.b64encode(open(test_png, 'rb').read()).decode('ascii')
    return 'data:image/png;base64,{}'.format(test_base64)

# Tab 2: By Account

# Calender Heatmap

@app.callback(
	Output('Heatmap','figure'),
	[Input('author','value'),Input('year','value')])

def plot_heatmap(author_v,year_v):
    tweets_hm1 = tweets_hm[(tweets_hm['author_name'] == author_v) & (tweets_hm['created_at'].dt.year == year_v)]\
        [['datetime','sum']] \
        .set_index('datetime')
    tweets_hm1.index = pd.DatetimeIndex(tweets_hm1.index)
    tweets_hm1 = tweets_hm1.resample('D').sum().reset_index()
    tweets_hm1['datetime'] = pd.to_datetime(tweets_hm1['datetime'], utc = True)
    tweets_hm1['weekday'] = tweets_hm1['datetime'].dt.weekday
    tweets_hm1['weeknumber'] = tweets_hm1['datetime'].dt.week

    #Format hover text
    text = ['Tweet Count: {} <br>Date: {} '.format(str(j),str(i)) for i, j in zip(tweets_hm1['datetime'].dt.date, tweets_hm1['sum'])]

    data = [
        go.Heatmap(
            y = tweets_hm1['weekday'],
            x = tweets_hm1['weeknumber'],
            z = tweets_hm1['sum'],
            text= text,
            hoverinfo='text',
            xgap=3,
            ygap=3,
            showscale=False,
            colorscale= 'reds'
        )
    ]

    layout = (
        go.Layout(
            title='Tweet Frequency <br> {} : {}'.format(author_v,year_v),
            height=300,
            yaxis=dict(ticks = '',
            showline = False, showgrid = False, zeroline = False,
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            tickvals=[0,1,2,3,4,5,6],
            ),
            xaxis=dict(ticks = '',
            showline = False, showgrid = False, zeroline = False,
            ticktext=[ 'Mon','January', 'Febuary', 'March', 'April', 'May',
            'June','July','August','September','October','November','December'],
            tickvals=[0,4,8,12,16,20,24,28,32,36,40,44,48,52],
            ),
            margin = dict(t=50,pad = 0),
        )
    )

    fig = go.Figure(data=data, layout=layout)
    fig.update_yaxes(autorange="reversed")
    return fig

# Plotly Tweet Tabel

@app.callback(
    Output('table', 'figure'),
    [Input('author','value')])

def update_table(author_v):
    tweets_hm2 = tweets_hm[tweets_hm['author_name'] == author_v][['created_at','message']]
    df = tweets_hm2.sort_values(by='created_at',ascending=False)
    fig1 = go.Figure(data=[go.Table(
    header=dict(values=list(df.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[df.created_at, df.message],
               fill_color='lavender',
               align='left'))
],
    layout = (
        go.Layout(title = '<b>tweets',
                  height=500,
                  margin = dict(t=55,b=0,r=0,l=0)
                  )))

    return fig1

# Tweet Word map

@app.callback(
    Output('Image', 'src'),
    [Input('author','value')])

def word_c(author_v):
    tweets_hm3 = tweets_hm[tweets_hm['author_name'] == author_v][['message']]
    text = tweets_hm3['message']
    wordcloud = WordCloud(
    width = 1000,
    height = 450,
    background_color = 'white',
    stopwords = STOPWORDS.update(['u00e7','u00f5es','u00e7o'])).generate(str(text))
    wordcloud.to_file('wc_author.png')
    test_png = 'wc_author.png'
    test_base64 = base64.b64encode(open(test_png, 'rb').read()).decode('ascii')
    return 'data:image/png;base64,{}'.format(test_base64)





if __name__ == '__main__':
    app.run_server(debug=False)
