# -*- coding: utf-8 -*-
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

import pandas as pd
from datetime import datetime as dt
import os
from spotipy import Spotify
import spotipy.util as util

from helpers import *

# ------------------------------------------------------------------------
# Setup
# ------------------------------------------------------------------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

username = os.getenv("SPOTIFY_USER_ID")
SCOPE = "user-library-read"
LIMIT = 50

token = util.prompt_for_user_token(username, SCOPE)
sp = Spotify(token)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title="Dash App")

r = sp.current_user_saved_tracks()
d = get_liked_songs(sp)
df = pd.DataFrame.from_dict(d)
df1 = df.iloc[:, 3:len(df.columns)]

# ------------------------------------------------------------------------
# Layout
# ------------------------------------------------------------------------
app.layout = html.Div([
        html.Div(id="hidden-div", style={"display":"none"}),
        html.H1("Spotify Liked Songs", style={"color":"#1DB954"}),
        dcc.DatePickerRange(
            id="my-date-picker-range",
            start_date = dt(2020, 8, 1),
            end_date = dt.today(),
            min_date_allowed = dt(2015, 9, 22),
            max_date_allowed = dt.today(),
            display_format="DD/MM/YYYY"
        ),
        html.Div([
            html.Div(children=[
                html.H6(id="num-tracks"), 
                html.P(children="Different Tracks")
                ]),
            html.Div([
                html.H6(id="num-artists"), 
                html.P(children="Different Artists")
                ]),
            html.Div([
                html.H6(id="num-albums"), 
                html.P(children="Different Albums")
                ]),
        ],
        id="figures-div"),
        html.Div([
            dcc.Input(
                id="playlist-name",
                placeholder='Playlist name... ',
                type='text',
                value=''
            )],
            id="playlist-div"), 
            html.Button("Create Playlist", id="button"),
        html.Div(id="my-table", 
                style={
                "width":"50%",
                "margin-left": "10%",
                "margin-right": "10%"}
    )],
    style={"textAlign": "center"}
)


# ------------------------------------------------------------------------
# Callbacks
# ------------------------------------------------------------------------
@app.callback(
        [Output("my-table", "children"),
        Output("num-tracks", "children"),
        Output("num-artists", "children"),
        Output("num-albums", "children")],
        [Input("my-date-picker-range", "start_date"),
        Input("my-date-picker-range", "end_date")]
)  
def update_info(start_date, end_date):
    dff = filter_songs(df, start_date, end_date)
    counts = dff.explode("Artist").nunique()
    return html.Div([generate_table(dff.iloc[:, 3:len(df.columns)])]), counts["Uri"], counts["Artist ID"], counts["Album ID"]

@app.callback(
    Output("hidden-div", "children"),
    [Input("button", "n_clicks")],
    [State("playlist-name", "value"),
    State("my-date-picker-range", "start_date"),
    State("my-date-picker-range", "end_date")]
)
def create_playlist(n_clicks, playlist_name, start_date, end_date):
    if n_clicks is not None and n_clicks > 0:
        dff = filter_songs(df, start_date, end_date)
        sorted_dff = dff.sort_values(by=["Added At"])
        uris_list = list(dff["Uri"])
        uris = [list(sorted_dff["Uri"][i:i+100]) for i in range(0, len(uris_list), 100)]
        r = sp.user_playlist_create(username, playlist_name)
        playlist_id = r["id"]
        for i in uris: 
            sp.user_playlist_add_tracks(username, playlist_id, i)
    
    return 

if __name__ == "__main__":
    app.run_server(debug=True)
