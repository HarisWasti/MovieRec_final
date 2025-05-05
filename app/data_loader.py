iimport pandas as pd
import joblib

def load_movie_meta():
    return pd.read_csv("data/movie_meta.csv")

def load_tfidf_matrix():
    return joblib.load("data/tfidf_matrix.pkl")
