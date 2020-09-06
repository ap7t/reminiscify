import dash_html_components as html
from datetime import datetime as dt

def get_liked_songs(sp, limit=50, total=250):
    offset = 0
    response = sp.current_user_saved_tracks(limit=limit, offset=offset)
    total = response['total']
    d = {"Uri":[], "Artist ID": [], "Album ID":[], "Artwork": [], "Track": [],"Artist": [],  "Album": [], "Added At": []}

    while offset < total:
        try:
            d["Uri"] += [response["items"][i]["track"]["uri"] for i in range(limit)]
            d["Artwork"] += [response["items"][i]["track"]["album"]["images"][2]["url"] for i in range(limit)]
            d["Track"] += [response["items"][i]["track"]["name"] for i in range(limit)]
            d["Artist"] += [response["items"][i]["track"]["artists"][0]["name"] for i in range(limit)]
            d["Artist ID"] += [response["items"][i]["track"]["artists"][0]["id"] for i in range(limit)]
            d["Album"] += [response["items"][i]["track"]["album"]["name"] for i in range(limit)]
            d["Album ID"] += [response["items"][i]["track"]["album"]["id"] for i in range(limit)]
            d["Added At"] += [dt.strptime(response["items"][i]["added_at"], "%Y-%m-%dT%XZ") for i in range(limit)] # use pd datetime
        except IndexError:
            pass

        offset += limit
        response = sp.current_user_saved_tracks(limit=limit, offset=offset)

    return d

def filter_songs(df, start_date, end_date):
    dff = df[(start_date < df['Added At']) & (df['Added At'] < end_date)]
    return dff

def generate_table(dataframe, max_rows=25):
    return html.Table([
            html.Thead(
                html.Tr([html.Th(col) for col in dataframe.columns])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(dataframe.iloc[i][col]) if col != "Artwork" else html.Img(src=dataframe.iloc[i][col]) for col in dataframe.columns
                ]) for i in range(min(max_rows, len(dataframe)))
            ])
        ])