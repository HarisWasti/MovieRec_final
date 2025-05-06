import pandas as pd

def load_movie_meta():
    return pd.read_csv("data/movie_meta.csv")
