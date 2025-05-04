import sqlite3
import pandas as pd
import joblib
from tqdm import tqdm
from rec_engine import hybrid_recommendations_by_title

# === Config ===
BATCH_SIZE = 500
DB_PATH = r"C:\Users\haris\OneDrive\Desktop\Streamlit\data\recommendations.db"
DATA_DIR = r"C:\Users\haris\OneDrive\Desktop\Streamlit\data"
MOVIE_META_PATH = f"{DATA_DIR}\\movie_meta.csv"

# === Load components ===
movie_meta = pd.read_csv(MOVIE_META_PATH)
tfidf_matrix = joblib.load(f"{DATA_DIR}\\tfidf_matrix.pkl")
user_movie_ratings = joblib.load(f"{DATA_DIR}\\user_movie_ratings.pkl")
item_movie_matrix = joblib.load(f"{DATA_DIR}\\item_movie_matrix.pkl")
knn = joblib.load(f"{DATA_DIR}\\knn_model.pkl")

# === Read existing titles once ===
with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recommendations (
        movie_title TEXT PRIMARY KEY,
        recommendations TEXT
    )
    ''')
    cursor.execute("SELECT movie_title FROM recommendations")
    existing_titles = set(row[0] for row in cursor.fetchall())

# === Get remaining titles ===
all_titles = movie_meta['title'].dropna().unique()
remaining_titles = [title for title in all_titles if title not in existing_titles]
print(f"📋 {len(remaining_titles)} movies left to process out of {len(all_titles)}")

# === Process in batches ===
for i in range(0, len(remaining_titles), BATCH_SIZE):
    batch = remaining_titles[i:i+BATCH_SIZE]
    print(f"\n⚙️ Processing batch {i//BATCH_SIZE + 1} ({len(batch)} movies)...")

    # Reconnect per batch (prevents lock issues)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for title in tqdm(batch, desc="→ Generating recs", leave=False):
            try:
                recs = hybrid_recommendations_by_title(
                    title,
                    movie_meta,
                    tfidf_matrix,
                    user_movie_ratings,
                    item_movie_matrix,
                    knn,
                    alpha=0.4,
                    top_n=20
                )
                if isinstance(recs, list) and recs[0] != "Movie title not found.":
                    rec_string = '|'.join(recs)
                    cursor.execute(
                        "INSERT OR REPLACE INTO recommendations (movie_title, recommendations) VALUES (?, ?)",
                        (title, rec_string)
                    )
            except Exception as e:
                print(f"❌ Error with '{title}': {e}")
                continue
        conn.commit()

    print(f"✅ Batch {i//BATCH_SIZE + 1} committed to DB")

print("🎉 All recommendations processed and saved.")
