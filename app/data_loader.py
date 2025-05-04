import os
import pandas as pd
import sqlite3

DATA_DIR = "data"

def load_movie_meta():
    return pd.read_csv(os.path.join(DATA_DIR, "movie_meta.csv"))

def get_recommendations_from_db(title, db_path=os.path.join(DATA_DIR, "recommendations.db")):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT recommendations FROM recommendations WHERE movie_title = ?", (title,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0].split('|')
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []
