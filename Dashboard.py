'''

@author Alec Holtzapfel
'''

import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import matplotlib.pyplot as plt
import plotly
import plotly.express as px

import json
import nltk
import pandas as pd
import seaborn as sns

from pathlib import Path
from wordcloud import WordCloud

from Modules.CleanData import DataCleaner
from Modules.MultiLabelClassification import MulitLabelClassification

def __get_valid_logins() -> dict[str,str]:
    with open(Path(Path.cwd(), 'config.json'), 'r') as file:
        configInfo = json.load(file)
        return configInfo["authentication"]

def __get_cleaned_data() -> pd.DataFrame:
    try:
        return pd.read_excel(
            Path(Path.cwd(), 'Cleaned Data', 'movie_data_with_predictions.xlsx'),
            engine = "openpyxl"
        )
    except FileNotFoundError:
            cleaner = DataCleaner()
            cleaner.run()

            mlc = MulitLabelClassification(cleaner.movieData)
            mlc.run()
            return mlc.movieData

def __convert_string_to_list_of_strings(value: str) -> list[str]:
    for char in ["[","]","'",")","("]:
        value = value.replace(char,"")
    value = value.split(",")
    genres = [
            value[i] for i in range(len(value))
        ]
    
    out = []
    for genre in genres:
        if genre != '':
            if genres[0] == genre:
                out.append(genre)
            else:
                out.append(genre[1:])
    return out

def __get_top_n_genres(df: pd.DataFrame, n: int):
    genre_freq = sum(df["Genres"].values.tolist(), [])
    genre_freq = nltk.FreqDist(genre_freq)

    simplified_genres = pd.DataFrame(
        {
            'Genre': list(genre_freq.keys()),
            'Freq': list(genre_freq.values())
        }
    )

    return simplified_genres.nlargest(
        columns="Freq",
        n=n
    )

def __get_top_n_genres(df: pd.DataFrame):
    genre_freq = sum(df["Genres"].values.tolist(), [])
    genre_freq = nltk.FreqDist(genre_freq)

    simplified_genres = pd.DataFrame(
        {
            'Genre': list(genre_freq.keys()),
            'Freq': list(genre_freq.values())
        }
    )

    return simplified_genres

def __get_top_n_terms(df: pd.DataFrame):
    term_freq = df["Summary"].values.tolist()
    term_freq = (' ').join(term_freq)
    term_freq = term_freq.split()
    term_freq = nltk.FreqDist(term_freq)

    terms = pd.DataFrame(
        {
            'Terms': list(term_freq.keys()),
            'Freq': list(term_freq.values())
        }
    )

    return terms

def __check_all_genre_accuracy_by_genre(df: pd.DataFrame, genre: str):
    actual = 0
    possible = 0
    for index in df.index:
        if genre in df["Genres"][index]:
            possible += 1
            if genre in df["Inferred Genres"][index]:
                actual+=1
    return [actual/possible, possible]

def __genrate_accuracy_df(df: pd.DataFrame):
    accuracy_df = {
        "Genre": [],
        "Frequency":[],
        "Accuracy":[]
    }

    all_genres = [
        genre for genres in df["Genres"].values.tolist() for genre in genres 
    ]

    for genre in list(set(all_genres)):
        [accuracy, frequency] = __check_all_genre_accuracy_by_genre(df, genre)
        accuracy_df["Genre"].append(genre)
        accuracy_df["Frequency"].append(frequency)
        accuracy_df["Accuracy"].append(accuracy)
        
    accuracy_df = pd.DataFrame(accuracy_df)
    return accuracy_df

def __create_word_cloud_by_genre(df: pd.DataFrame, genre: str):
    words = []
    for index in df.index:
        if genre in df["Genres"][index]:
            words.append(df["Summary"][index])
            
    words = (' ').join(words)
    words = words.split()

    out = {
        "Term": list(set(words)),
        "Count": []
    }

    for key in out["Term"]:
        i = 0
        for word in words:
            if word == key:
                i+=1
        out["Count"] = i

    return pd.DataFrame(out)

app = dash.Dash(__name__)

auth = dash_auth.BasicAuth(
    app,
    __get_valid_logins()
)

df = __get_cleaned_data()

for column in ["Genres", "Simplified Genres", "Inferred Genres", "Inferred Simplified Genres"]:
    df[column] = df[column].apply(lambda x: __convert_string_to_list_of_strings(x))

genre_freq_df = __get_top_n_genres(df)
term_freq_df = __get_top_n_terms(df)
accuracy_df = __genrate_accuracy_df(df)


app.layout = html.Div([
    html.H1('Holtzapfel Streaming Service'),
    dcc.Input(placeholder="Please input a number", type="number", id='Genre Integer Input'),
    dcc.Graph(id='genre_graph'),
    dcc.Input(placeholder="Please input a number", type="number", id='Term Integer Input'),
    dcc.Graph(id='term_graph'),
    dcc.Input(placeholder="Please input a number", type="number", id='Term Inf Integer Input'),
    dcc.Graph(id='term_inf_graph'),
    dcc.Input(placeholder="Please input a number", type="number", id='acc int input'),
    dcc.Graph(id='acc_graph')
], className='container')

@app.callback(
    dash.dependencies.Output('genre_graph', 'figure'),
    [dash.dependencies.Input('Genre Integer Input', 'value')])
def update_graph(input_value):
    if input_value:
        data = genre_freq_df.nlargest(
            columns="Freq",
            n=input_value
        )
        return px.bar(data, x="Genre", y="Freq", title=f"Top {input_value} Genres")
    else:
        data = genre_freq_df.nlargest(
            columns="Freq",
            n=50
        )
        return px.bar(data, x="Genre", y="Freq", title="Top 50 Genres")

@app.callback(
    dash.dependencies.Output('term_graph', 'figure'),
    [dash.dependencies.Input('Term Integer Input', 'value')])
def update_graph(input_value):
    if input_value:
        data = term_freq_df.nlargest(
            columns="Freq",
            n=input_value
        )
        return px.bar(data, x="Terms", y="Freq", title=f"Top {input_value} Terms")
    else:
        data = term_freq_df.nlargest(
            columns="Freq",
            n=50
        )
        return px.bar(data, x="Terms", y="Freq", title="Top 50 Terms")

@app.callback(
    dash.dependencies.Output('term_inf_graph', 'figure'),
    [dash.dependencies.Input('Term Inf Integer Input', 'value')])
def update_graph(input_value):
    if input_value:
        data = term_freq_df.nsmallest(
            columns="Freq",
            n=input_value
        )
        return px.bar(data, x="Terms", y="Freq", title=f"Top {input_value} Infrequent Terms")
    else:
        data = term_freq_df.nsmallest(
            columns="Freq",
            n=10
        )
        return px.bar(data, x="Terms", y="Freq", title="Top 10 Infrequent Terms")

@app.callback(
    dash.dependencies.Output('acc_graph', 'figure'),
    [dash.dependencies.Input('acc int input', 'value')])
def update_graph(input_value):
    if input_value:
        data = accuracy_df.nlargest(
            columns="Frequency",
            n=input_value
        )
        return px.scatter(data, x="Terms", y="Accuracy", title=f"Top {input_value} Accuracy vs Frequency")
    else:
        data = accuracy_df.nlargest(
            columns="Frequency",
            n=10
        )
        return px.scatter(data, x="Frequency", y="Accuracy", title="Top 50 Accuracy vs Frequency")

if __name__ == '__main__':
    app.run_server(debug=True)
    
