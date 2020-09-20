import dash_html_components as html
import pandas as pd

def get_liked_songs(sp, limit=50):
    offset = 0
    response = sp.current_user_saved_tracks(limit=limit, offset=offset)
    total = response['total']
    # total = 500
    d = {"Uri":[], "Artist ID": [], "Album ID":[], "Artwork": [], "Track": [],
        "Artist": [], "Album": [], "Added At": []}

    # do label with album stuff

    while offset < total:
        try:
            d["Uri"] += [response["items"][i]["track"]["uri"] for i in range(limit)]
            d["Artwork"] += [response["items"][i]["track"]["album"]["images"][2]["url"] for i in range(limit)]
            d["Track"] += [response["items"][i]["track"]["name"] for i in range(limit)]
            d["Artist"] += [response["items"][i]["track"]["artists"][0]["name"] for i in range(limit)]
            d["Artist ID"] += [response["items"][i]["track"]["artists"][0]["id"] for i in range(limit)]
            d["Album"] += [response["items"][i]["track"]["album"]["name"] for i in range(limit)]
            d["Album ID"] += [response["items"][i]["track"]["album"]["id"] for i in range(limit)] # do it this way so can be used in album endpoint
            d["Added At"] += [response["items"][i]["added_at"] for i in range(limit)] # use pd datetime
        except IndexError:
            pass

        offset += limit
        response = sp.current_user_saved_tracks(limit=limit, offset=offset)
    
    df = pd.DataFrame.from_dict(d)
    df["Added At"] = pd.to_datetime(df["Added At"])
    return df

def get_saved_albums(sp, limit=20):
    offset = 0
    response = sp.current_user_saved_albums(limit=limit, offset=offset)
    total = response['total']
    total = 500
    d = {"Artist ID": [], "Album ID":[], "Artwork": [], "Artist": [], "Album": [],"Label": [], "Added At": []}

    # do label with album stuff

    while offset < total:
        try:
            d["Artwork"] += [response["items"][i]["album"]["images"][2]["url"] for i in range(limit)]
            d["Artist"] += [response["items"][i]["album"]["artists"][0]["name"] for i in range(limit)]
            d["Artist ID"] += [response["items"][i]["album"]["artists"][0]["id"] for i in range(limit)]
            d["Album"] += [response["items"][i]["album"]["name"] for i in range(limit)]
            d["Album ID"] += [response["items"][i]["album"]["id"] for i in range(limit)] # do it this way so can be used in album endpoint
            d["Label"] += [response["items"][i]["album"]["label"] for i in range(limit)]
            d["Added At"] += [response["items"][i]["added_at"] for i in range(limit)] # use pd datetime
        except IndexError:
            pass

        offset += limit
        response = sp.current_user_saved_albums(limit=limit, offset=offset)
    
    
    df = pd.DataFrame.from_dict(d)
    df["Added At"] = pd.to_datetime(df["Added At"])
    return df

def filter_songs(df, start_date, end_date):
    dff = df[(start_date <= df['Added At']) & (df['Added At'] <= end_date)]
    return dff



def generate_table(dataframe, max_rows=25):
    # dataframe["Added"]
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