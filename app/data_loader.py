import os
import pandas as pd
import sqlite3

# Absolute path to the `data/` folder (safe across environments)
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
MOVIE_META_PATH = os.path.join(DATA_DIR, "movie_meta.csv")
DB_PATH = os.path.join(DATA_DIR, "recommendations.db")

import os
import time
import pandas as pd

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
MOVIE_META_PATH = os.path.join(DATA_DIR, "movie_meta.csv")

def load_movie_meta(retries=3, delay=1.5):
    for attempt in range(retries):
        try:
            if not os.path.exists(MOVIE_META_PATH):
                raise FileNotFoundError(f" movie_meta.csv not found at: {MOVIE_META_PATH}")

            if os.path.getsize(MOVIE_META_PATH) < 100:
                raise ValueError(" File too small to be valid — waiting for proper mount...")

            df = pd.read_csv(MOVIE_META_PATH)
            if df.empty or len(df.columns) < 3:
                raise ValueError(" CSV file loaded but has no columns or data.")
            
            print(f" movie_meta.csv loaded with shape: {df.shape}")
            return df

        except Exception as e:
            print(f" Attempt {attempt+1}/{retries} failed: {e}")
            time.sleep(delay)

    raise RuntimeError(" Failed to load movie_meta.csv after retries.")



def get_recommendations_from_db(title, db_path=DB_PATH):
    try:
        print(f" Looking up: {title} in {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT recommendations FROM recommendations WHERE movie_title = ?", (title,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0].split('|')
        return []
    except Exception as e:
        print(f" DB error: {e}")
        return []
