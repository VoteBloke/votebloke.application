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

keys = generate_keys()
post_new_elections(keys, 'test1', ['opcja1', 'opcja2'])
els = get_active_elections().text

