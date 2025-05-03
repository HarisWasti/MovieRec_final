import os
import requests
import joblib
import pandas as pd

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

FILES = {
    "movie_meta.csv": "https://1drv.ms/x/c/db1fd89b1b4b1003/EazXL6SxPY1FkTOdmWLSONUBpBgcp5iNAfREHq0SuIvFlQ?e=grKbKJ",
    "tfidf_matrix.pkl": "https://1drv.ms/u/c/db1fd89b1b4b1003/EVG4OzuqenVNhULl2X6cmBkB7480jSVYAircD2xFFD5dtQ?e=lpZdYy",
    "user_movie_ratings.pkl": "https://1drv.ms/u/c/db1fd89b1b4b1003/EQ2sE32_Vt1Blsb_jWKSZ4wBxm8vBcEnB3e5rmIlr11hrg?e=okeeTG",
    "item_movie_matrix.pkl": "https://1drv.ms/u/c/db1fd89b1b4b1003/EZRiwHAWPeBOuMgodFYrWTQBhsBXb8RQXzNJSGCJQQAGCA",
    "knn_model.pkl": "https://1drv.ms/u/c/db1fd89b1b4b1003/ESrQLm8v_kFGiOXCuJttbdkBGX2sCCZScdcQONZzTvaMxg?e=5IE9HG"
}

def download_file(name, url):
    local_path = os.path.join("data", name)
    if os.path.exists(local_path):
        return local_path

    print(f"Downloading {name} from OneDrive...")

    # Follow OneDrive redirect
    response = requests.get(url, allow_redirects=True)
    
    # Check if content looks like HTML (i.e., a failed redirect)
    if "html" in response.text[:100].lower():
        raise ValueError(f"{name} did not download properly — got HTML instead of CSV. Check the link.")

    with open(local_path, "wb") as f:
        f.write(response.content)

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
