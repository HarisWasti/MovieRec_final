import os
import sqlite3
import pandas as pd
import joblib
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

# Config
DATA_DIR = r"C:\Users\haris\OneDrive\Desktop\Streamlit\data"
DB_PATH = os.path.join(DATA_DIR, "recommendations.db")
MOVIE_META_PATH = os.path.join(DATA_DIR, "movie_meta.csv")
BATCH_SIZE = 1000
NUM_WORKERS = max(cpu_count() - 1, 2)

# Shared globals (loaded in each worker)
movie_meta = None
tfidf_matrix = None
user_movie_ratings = None
item_movie_matrix = None
knn = None

def init_worker():
    global movie_meta, tfidf_matrix, user_movie_ratings, item_movie_matrix, knn
    movie_meta = pd.read_csv(MOVIE_META_PATH)
    tfidf_matrix = joblib.load(os.path.join(DATA_DIR, "tfidf_matrix.pkl"))
    user_movie_ratings = joblib.load(os.path.join(DATA_DIR, "user_movie_ratings.pkl"))
    item_movie_matrix = joblib.load(os.path.join(DATA_DIR, "item_movie_matrix.pkl"))
    knn = joblib.load(os.path.join(DATA_DIR, "knn_model.pkl"))

def process_movie(title):
    from rec_engine import hybrid_recommendations_by_title
    try:
        recs = hybrid_recommendations_by_title(
            title,
            movie_meta,
            tfidf_matrix,
            user_movie_ratings,
            item_movie_matrix,
            knn,
            alpha=0.6,
            top_n=9
        )

        if isinstance(recs, list) and recs[0] != "Movie title not found.":
            return (title, '|'.join(recs))
    except:
        return None
    return None

if __name__ == "__main__":
    all_meta = pd.read_csv(MOVIE_META_PATH)
    all_titles = all_meta['title'].dropna().unique()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS recommendations (
                   movie_title TEXT PRIMARY KEY,
                   recommendations TEXT
               )'''
        )
        cursor.execute("SELECT movie_title FROM recommendations")
        existing_titles = set(row[0] for row in cursor.fetchall())

    remaining_titles = [title for title in all_titles if title not in existing_titles]
    print(f"{len(remaining_titles)} movies left to process out of {len(all_titles)}")

    for i in range(0, len(remaining_titles), BATCH_SIZE):
        batch = remaining_titles[i:i + BATCH_SIZE]
        print(f"Batch {i // BATCH_SIZE + 1}: Processing {len(batch)} movies...")

        with Pool(NUM_WORKERS, initializer=init_worker) as pool:
            results = list(tqdm(pool.imap(process_movie, batch), total=len(batch)))

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            for row in results:
                if row:
                    cursor.execute(
                        "INSERT OR REPLACE INTO recommendations (movie_title, recommendations) VALUES (?, ?)", row
                    )
            conn.commit()

        print(f"Batch {i // BATCH_SIZE + 1} committed")

    print("All recommendations processed and saved.")
