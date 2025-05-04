import os
import gdown
import pandas as pd
import joblib

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# OneDrive URLs (converted to gdown-compatible URLs using IDs)
FILES = {
    "movie_meta.csv":     "https://drive.google.com/uc?id=1K1k2fLwWu5xajBp2iuwtl0IICJc-5Mq4",
    "tfidf_matrix.pkl":   "https://drive.google.com/uc?id=1lja74H2YBPr5Tcm4UqKC4-YoIPHlRWzI",
    "user_movie_ratings.pkl": "https://drive.google.com/uc?id=1IaUqZmDGqUdxE3qced90h0Nkw0i0ZXKZ",
    "item_movie_matrix.pkl":  "https://drive.google.com/uc?id=1wbBR92AYCCYciOnk1FaOvqBlszWK-lN4",
    "knn_model.pkl":      "https://drive.google.com/uc?id=1caQ2s0bwzgON5mIs-LigIomZlS0sIgvs"
}

def download_file(name, url):
    local_path = os.path.join(DATA_DIR, name)
    if not os.path.exists(local_path):
        print(f"📦 Downloading {name}...")
        gdown.download(url, local_path, quiet=False)
    return local_path

def load_all_data():
    paths = {name: download_file(name, url) for name, url in FILES.items()}
    return {
        "movie_meta": pd.read_csv(paths["movie_meta.csv"]),
        "tfidf_matrix": joblib.load(paths["tfidf_matrix.pkl"]),
        "user_movie_ratings": joblib.load(paths["user_movie_ratings.pkl"]),
        "item_movie_matrix": joblib.load(paths["item_movie_matrix.pkl"]),
        "knn": joblib.load(paths["knn_model.pkl"])
    }
