import os
import pandas as pd
import sqlite3

# Absolute path to the `data/` folder (safe across environments)
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
MOVIE_META_PATH = os.path.join(DATA_DIR, "movie_meta.csv")
DB_PATH = os.path.join(DATA_DIR, "recommendations.db")

def load_movie_meta():
    print(f"📁 Trying to load movie_meta.csv from: {MOVIE_META_PATH}")

    if not os.path.exists(MOVIE_META_PATH):
        raise FileNotFoundError(f"❌ File not found: {MOVIE_META_PATH}")

    size = os.path.getsize(MOVIE_META_PATH)
    print(f"✅ File exists — Size: {size} bytes")

    with open(MOVIE_META_PATH, "r", encoding="utf-8") as f:
        preview = f.read(300)
        print("📄 File preview:")
        print(preview[:300])

    try:
        df = pd.read_csv(MOVIE_META_PATH)
        print(f"✅ Loaded CSV with shape: {df.shape}")
        print(f"🧠 Columns: {df.columns.tolist()}")
        return df
    except Exception as e:
        print("❌ pandas.read_csv() failed!")
        raise e


def get_recommendations_from_db(title, db_path=DB_PATH):
    try:
        print(f"🔍 Looking up: {title} in {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT recommendations FROM recommendations WHERE movie_title = ?", (title,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0].split('|')
        return []
    except Exception as e:
        print(f"❌ DB error: {e}")
        return []
