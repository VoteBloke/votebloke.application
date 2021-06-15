import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import *
import plotly.graph_objects as go
import base64
import numpy as np

from communications import *
from cryptography_wrappers import *
from helper_functions import *

logged_in = False
private_key = None

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.GRID]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    prevent_initial_callbacks=True
)

app.layout = html.Div(id='page_content', className='app_body', children=[

    dbc.Row(
        [
            dbc.Col(
                [
                    html.P(id='placeholder'),
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
                    dbc.Row(
                        [
                            dcc.Markdown(
                                id='logStatus',
                                children=
                                '''
                                ### Not logged in!\n
                                #### Upload the key pair or generate a new one
                                '''
                            ),
                            html.Button(
                                'Download the active key',
                                id='download_private_key',
                                n_clicks=0
                            ),
                            dcc.Download(id='private_key_download_action')
                        ]
                    ),
                    dbc.Row(),
                    html.H3(children='Logging in'),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Upload(
                                    id='upload_private_key',
                                    children=html.Div(
                                        [
                                            html.A('Select a file')
                                        ]
                                    )
                                )
                            ),
                            dbc.Col(html.H4(children='OR')),
                            dbc.Col(
                                html.Button(
                                    'Generate a new key pair',
                                    id='newPair',
                                    n_clicks=0
                                )
                            ),
                        ]
                    ),
                    html.Div(id='inputBar', children=[
                        html.H2(children='Cast a vote'),
                        html.Button(
                            'Load available elections',
                            id='voter_get_elections',
                            n_clicks=0
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
                            id='cast_vote',
                            n_clicks=0
                        ),
                        dcc.Markdown(
                            id='cast_status'
                        ),
                        dbc.Row(),
                        dbc.Row(html.H2(children='Create elections')),
                        dbc.Row(html.Label('Provide a name')),
                        dbc.Row(dcc.Input(id='election_name', type='text', value='Election Name')),
                        dbc.Row(html.Label('Provide options separated by a semicolon(;)')),
                        dbc.Row(html.Div(id='options_summary')),
                        dcc.Input(id='electionOptions', type='text', value='Option 1; Option 2; Option 3;...'),
                        html.Button(
                            'Create elections',
                            id='create_elections',
                            n_clicks=0
                        ),
                        dcc.Markdown(
                            id='create_elections_status'
                        ),
                        html.H2(children='Close elections'),
                        html.Button(
                            'Load available elections',
                            id='closer_get_elections',
                            n_clicks=0
                        ),

                        html.Label('Select elections'),
                        dcc.Dropdown(
                            id='close_active_elections',
                            options=[]
                        ),
                        html.Button(
                            'Close',
                            id='close_elections',
                            n_clicks=0
                        ),
                        dcc.Markdown(
                            id='closing_status'
                        ),
                    ]),
                ]
            ),
            dbc.Col(
                [
                    html.H4(children='Select elections to view the results'),
                    html.Button(
                        'Load available elections',
                        id='tally_get_elections',
                        n_clicks=0
                    ),
                    dcc.Dropdown(
                        id='elections',
                        options=[]
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


# add callback for logging in
@app.callback(
    Output(component_id='logStatus', component_property='children'),
    Input(component_id='newPair', component_property='n_clicks')
)
def create_new_account(n_clicks):
    global private_key
    private_key = create_account()
    global logged_in
    logged_in = True
    return '''
    ## Logged In!
    '''


# create a callback for downloading the active private key
@app.callback(
    Output(component_id='private_key_download_action', component_property='data'),
    Input(component_id='download_private_key', component_property='n_clicks')
)
def download_private_key(n_clicks):
    global private_key
    return {'content': export_private_key(private_key).decode('ascii'), 'filename': 'privateKey.pem'}


# create a callback for uploading private key
@app.callback(
    Output(component_id='placeholder', component_property='children'),
    Input(component_id='upload_private_key', component_property='contents')
)
def digest_private_key(conts):
    priv_key_string = conts.split(',')[-1]
    priv_key_string = base64.b64decode(priv_key_string)

    global private_key
    global logged_in

    private_key = import_private_key(priv_key_string)
    logged_in = True

    return

# legacy elections creating
@app.callback(
    Output(component_id='create_elections_status', component_property='children'),
    Input(component_id='create_elections', component_property='n_clicks'),
    State(component_id='election_name', component_property='value'),
    State(component_id='electionOptions', component_property='value')
)
def create_elections(clicks, name, options):
    global logged_in
    global private_key
    if not logged_in:
        return '''
        Please log in first
        '''
    opts = options.split('; ')
    req = post_new_elections(private_key, name, opts)

    if req.status_code != 200:
        return '''
        ### Error!
        '''
    return '''
    ### Elections created successfully!
    '''


# create a callback for reading open elections list
@app.callback(
    Output(component_id='activeElections', component_property='options'),
    Input(component_id='voter_get_elections', component_property='n_clicks')
)
def get_elections_vote(n_clicks):
    req = get_active_elections()

    if req.status_code != 200:
        return []

    return parse_active_elections(req)


# update voting options based on selected elections
@app.callback(
    Output(component_id='votingOptions', component_property='options'),
    Input(component_id='activeElections', component_property='value')
)
def get_options_vote(elections):
    req = get_active_elections()
    if req.status_code != 200:
        return []

    opts = json.loads(req.text)

    for i in opts:
        if i['transactionId'] == elections:
            res = [{'label': j, 'value': j} for j in i['entryMetadata']['answers']]

    return res


# cast a vote
@app.callback(
    Output(component_id='cast_status', component_property='children'),
    Input(component_id='cast_vote', component_property='n_clicks'),
    State(component_id='activeElections', component_property='value'),
    State(component_id='votingOptions', component_property='value')
)
def vote(clicks, election_id, option):
    global private_key

    tmp = cast_vote(private_key, election_id, option)

    if tmp.status_code != 200:
        return '''
        #### Error!
        '''
    return '''
    #### OK!
    '''

@app.callback(
    Output(component_id='close_active_elections', component_property='options'),
    Input(component_id='closer_get_elections', component_property='n_clicks')
)
def get_elections_close(n_clicks):
    req = get_active_elections()

    if req.status_code != 200:
        return []

    return parse_active_elections(req)

@app.callback(
    Output(component_id='closing_status', component_property='children'),
    Input(component_id='close_elections', component_property='n_clicks'),
    State(component_id='close_active_elections', component_property='value')
)
def close(clicks, election_id):
    global private_key

    tmp = tally_elections(private_key, election_id)

    if tmp.status_code != 200:
        return '''
        #### Error in closing elections!
        '''
    return '''
    #### Elections closed successfully
    '''

@app.callback(
    Output(component_id='elections', component_property='options'),
    Input(component_id='tally_get_elections', component_property='n_clicks')
)
def get_elections_tally(n_clicks):
    req = get_output_transactions()

    if req.status_code != 200:
        return []

    ret = json.loads(req.text)
    ret = [i for i in ret if i['entryType'] == 'tally']

    ret = [{'label': i['entryMetadata']['question'][0], 'value': i['entryMetadata']['question'][0]} for i in ret]

    return ret


@app.callback(
    Output(component_id='fig_outp', component_property='figure'),
    Input(component_id='elections', component_property='value')
)
def create_graph(elections_id):
    # define a layout of returning figure

    # tally selected elections
    global private_key
    req = get_output_transactions();

    if req.status_code != 200:
        print("Error")

    transactions_list = json.loads(req.text)
    transactions_list = [i for i in transactions_list if i['entryType'] == 'tally']

    x = None
    y = None

    for i in transactions_list :
        if i['entryMetadata']['question'][0] == elections_id :
            xs = i['entryMetadata']['answers']
            ys = [int(j) for j in i['entryMetadata']['voteCounts']]
            break

    fig = go.Figure(
        data = go.Bar(
            x = xs,
            y = ys
        ),
        layout=go.Layout(
            template='simple_white',
            xaxis=dict(
                title=dict(
                    text=''
                ),
            ),
            yaxis=dict(
                title=dict(
                    text='# of votes'
                ),
                dtick = 1
            ),
            height=700
        )
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=21317)