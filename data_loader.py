import os
import gdown
import pandas as pd
import joblib

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

GDRIVE_FILES = {
    "movie_meta.csv": "1K1k2fLwWu5xajBp2iuwtl0IICJc-5Mq4",
    "tfidf_matrix.pkl": "1lja74H2YBPr5Tcm4UqKC4-YoIPHlRWzI",
    "user_movie_ratings.pkl": "1IaUqZmDGqUdxE3qced90h0Nkw0i0ZXKZ",
    "item_movie_matrix.pkl": "1wbBR92AYCCYciOnk1FaOvqBlszWK-lN4",
    "knn_model.pkl": "1Yd5ucjTGxD9L4x1FYElPyil-f5uQHc4w"
}

def download_from_gdrive(name, file_id):
    local_path = os.path.join(DATA_DIR, name)
    if not os.path.exists(local_path):
        print(f"📦 Downloading {name} from Google Drive...")
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, local_path, quiet=False)
    return local_path

def load_all_data():
    paths = {name: download_from_gdrive(name, fid) for name, fid in GDRIVE_FILES.items()}

    return {
        "movie_meta": pd.read_csv(paths["movie_meta.csv"]),
        "tfidf_matrix": joblib.load(paths["tfidf_matrix.pkl"]),
        "user_movie_ratings": joblib.load(paths["user_movie_ratings.pkl"]),
        "item_movie_matrix": joblib.load(paths["item_movie_matrix.pkl"]),
        "knn": joblib.load(paths["knn_model.pkl"])
    }
