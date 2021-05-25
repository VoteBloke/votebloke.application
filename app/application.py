import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import pandas as pd
from dash.dependencies import Input, Output, State
from communications import *
import plotly.graph_objects as go
import socket

from dash_table import DataTable

# read torch models


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.GRID]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
loggedIn = False

app.layout = html.Div(id='page_content', className='app_body', children=[

    dbc.Row(
        [
            dbc.Col(
                [
                    html.H1(children='Votebloke'),
                    html.H5(children='A distributed voting platform'),
                ]
            ),
        ]
    ),
    dbc.Row(html.H1()),
    dbc.Row(
        [
            dbc.Col(
                [
                    dcc.Markdown(
                        id = 'logStatus',
                        children =
                        '''
                        ### Not logged in!\n
                        #### Upload the key pair or generate a new one
                        '''
                    ),
                    dbc.Row(),
                    html.H3(children='Logging in'),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Upload(
                                    id = 'keyPair',
                                    children = html.Div(
                                        [
                                            html.A('Select a file')
                                        ]
                                    )
                                )
                            ),
                            dbc.Col(html.H4(children = 'OR')),
                            dbc.Col(
                                html.Button(
                                    'Generate a new key pair',
                                    id = 'newPair',
                                    n_clicks = 0
                                )
                            )
                        ]
                    ),
                    html.Div(id='inputBar', children=[
                        html.H2(children='Cast a vote'),
                        html.Button(
                            'Load available elections',
                            id = 'voter_get_elections',
                            n_clicks = 0
                        ),

                        html.Label('Select elections'),
                        dcc.Dropdown(
                            id='activeElections',
                            options=[]
                        ),

                        html.Label('Select an option'),
                        dcc.Dropdown(
                            id='votingOptions',
                            options=[],
                        ),
                        html.Button(
                            'Vote',
                            id = 'cast_vote',
                            n_clicks = 0
                        ),
                        dcc.Markdown(
                            id = 'cast_status'
                        ),
                        dbc.Row(),
                        html.H2(children = 'Create elections'),
                        html.Label('Provide a name'),
                        dcc.Input(id = 'electionName', type = 'text', value = 'Election Name'),
                        html.Label('Provide options separated by a semicolon(;)'),
                        dcc.Input(id = 'electionOptions', type = 'text', value = 'Option 1; Option 2; Option 3;...'),
                        html.Button(
                            'Create elections',
                            id = 'create_elections',
                            n_clicks = 0
                        ),
                        dcc.Markdown(
                            id = 'create_elections_status'
                        )
                    ]),
                ]
            ),
            dbc.Col(
                [
                    html.H4(children='Select elections to view the results'),
                    html.Button(
                        'Load available elections',
                        id = 'tally_get_elections',
                        n_clicks = 0
                    ),
                    dcc.Dropdown(
                        id = 'elections',
                        options = []
                    ),
                    html.Div(id='election_results', children=[
                        html.H2(children='Results'),
                        dcc.Graph(id='fig_outp'),
                    ])
                ]
            )
        ]
    )
])

#add callback for logging in
@app.callback(
    Output(component_id = 'logStatus', component_property = 'children'),
    Input(component_id = 'newPair', component_property = 'n_clicks')
)
def create_new_account(n_clicks) :

    if n_clicks == 0:
        return '''
        ### Not logged in!\n
        #### Upload the key pair or generate a new one
        '''

    res = create_account()

    if res.status_code != 200 :
        return '''
        ## Error!
        '''
    global loggedIn
    loggedIn = True
    return '''
    ## Successfully logged in!
    '''

#create callback for submitting new elections
@app.callback(
    Output(component_id = 'create_elections_status', component_property = 'children'),
Input(component_id = 'create_elections', component_property = 'n_clicks'),
    State(component_id = 'electionName', component_property = 'value'),
    State(component_id = 'electionOptions', component_property = 'value')
)
def create_elections(clicks, name, options) :
    if clicks == 0:
        return ''''''

    global loggedIn
    if not loggedIn :
        return '''
        Please log in first
        '''
    opts = options.split('; ')
    req = post_new_elections(name, opts)

    if req.status_code != 200 :
        return '''
        ### Error!
        '''
    return '''
    ### Elections created successfully!
    '''

#create a callback for reading open elections list
@app.callback(
    Output(component_id = 'activeElections', component_property = 'options'),
    Input(component_id = 'voter_get_elections', component_property = 'n_clicks')
)
def get_elections_vote(n_clicks) :
    req = get_active_elections()

    if req.status_code != 200 :
        return []

    opts = json.loads(req.text)

    res = [{'label': i['entryMetadata']['question'][0], 'value': i['transactionId']} for i in opts]

    return res

#update voting options based on selected elections
@app.callback(
    Output(component_id = 'votingOptions', component_property = 'options'),
    Input(component_id = 'activeElections', component_property = 'value')
)
def get_options_vote(elections) :

    req = get_active_elections()
    if req.status_code != 200 :
        return []

    opts = json.loads(req.text)

    res = []

    for i in opts :
        if i['transactionId'] == elections :
            res = [{'label': j, 'value': j} for j in i['entryMetadata']['answers']]

    return res

#cast a vote
@app.callback(
    Output(component_id = 'cast_status', component_property = 'children'),
    Input(component_id = 'cast_vote', component_property = 'n_clicks'),
    State(component_id = 'activeElections', component_property = 'value'),
    State(component_id = 'votingOptions', component_property = 'value')
)
def vote(clicks, election_id, option) :
    tmp = cast_vote(election_id, option)

    if tmp.status_code != 200 :
        return '''
        #### Error!
        '''
    return '''
    #### OK!
    '''

@app.callback(
    Output(component_id = 'elections', component_property = 'options'),
    Input(component_id = 'tally_get_elections', component_property = 'value')
)
def get_options_vote(elections) :

    req = get_active_elections()
    if req.status_code != 200 :
        return []

    opts = json.loads(req.text)

    res = []

    for i in opts :
        if i['transactionId'] == elections :
            res = [{'label': j, 'value': j} for j in i['entryMetadata']['answers']]

    return res

@app.callback(
    Output(component_id = 'fig_outp', component_property = 'figure'),
    Input(component_id = 'elections', component_property = 'value')
)
def create_graph(electionsID):
    # define a layout of returning figure

    fig = go.Figure(
        layout=go.Layout(
            template='simple_white',
            xaxis=dict(
                title=dict(
                    text=''
                ),
                range=[0, 5]
            ),
            yaxis=dict(
                title=dict(
                    text='# of votes'
                ),
            ),
            height=700
        )
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=21317)