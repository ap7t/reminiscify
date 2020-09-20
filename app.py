# -*- coding: utf-8 -*-
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

import pandas as pd
from collections import Counter
import plotly.express as px
from datetime import datetime as dt, date, timedelta
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

token = util.prompt_for_user_token(username, SCOPE)
sp = Spotify(token)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title="Reminiscify")

r = sp.current_user_saved_tracks()
df = get_liked_songs(sp)

# df = pd.read_csv("liked_songs.csv")
df["Added At"] = pd.to_datetime(df["Added At"])
df["Day Num"] = df["Added At"].dt.weekday
df["Day"] = df["Added At"].dt.day_name()

days_df = df.groupby(["Day Num", "Day"]).size().reset_index(name="Songs Saved")

fig = px.bar(days_df, x="Day", y="Songs Saved")

# ------------------------------------------------------------------------
# Layout
# ------------------------------------------------------------------------
app.layout = html.Div([
        html.Div(id="hidden-div", style={"display":"none"}),
        html.H1("Reminiscify", style={"color":"#1DB954"}),

        dcc.DatePickerRange(
            id="my-date-picker-range",
            start_date = date(2020, 9, 1),
            end_date =date.today(),
            min_date_allowed = dt(2015, 9, 22),
            max_date_allowed = date.today(),
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
                ])
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
        dcc.Graph(
        id="days-graph",
        figure=fig
        ),
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
        Output("num-albums", "children"),
        Output('days-graph', 'figure')],
        [Input("my-date-picker-range", "start_date"),
        Input("my-date-picker-range", "end_date")]
)  
def update_info(start_date, end_date):
    dff = filter_songs(df, start_date, end_date)
    dff["Added At"] = dff["Added At"].dt.strftime("%c") # nice readable datetime format (done after filter_songs func as need as datetime for that func)
    
    # if no songs saved on a day without following code the bar chart only shows days with things saved
    # update the dataframe to include an entry for all days so the graph always has every day on the x axis
    week_days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
    days_df = dff.groupby(["Day Num", "Day"]).size().reset_index(name="Songs Saved")
    for i, day in enumerate(week_days):
        if day not in list(days_df["Day"]):
            days_df.loc[len(days_df)] = [i, day, 0]

    start_dt= dt.strptime(start_date, "%Y-%m-%d")
    end_dt =   dt.strptime(end_date, "%Y-%m-%d")
    start_weekday = int(start_dt.weekday())
    end_weekday = int(end_dt.weekday())
    
    # remove entries for days that don't exist between selected date range if range is in the same week 
    days_between = end_dt - start_dt
    if days_between.days < 7:
        days_df = days_df[days_df["Day Num"].isin([i for i in range(start_weekday, end_weekday + 1)])]
    
    # the face im using datetime for the end date fucking me up nmust fix tomorrow

    days_df.sort_values(by=["Day Num"], inplace=True)
    days_df.drop(labels=["Day Num"], axis=1, inplace=True)

    fig = px.bar(days_df, x="Day", y="Songs Saved")
    fig.update_layout(transition_duration=250)
    
    counts = dff.explode("Artist").nunique() # come back to artists 

    dff = dff.drop(labels=["Uri", "Artist ID", "Album ID", "Day", "Day Num"], axis=1)
    return html.Div([generate_table(dff)]), counts["Uri"], counts["Artist ID"], counts["Album ID"], fig

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
