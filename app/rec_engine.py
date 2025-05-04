import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import json

def search_movie(title_input, movie_meta):
    title_input = title_input.lower()
    filtered = movie_meta[movie_meta['title'].str.lower().str.contains(title_input, regex=False)]
    return filtered['title'].iloc[0] if not filtered.empty else None

# 🧠 For real-time user input
def hybrid_recommendations(title_input, movie_meta, tfidf_matrix, user_movie_ratings, item_movie_matrix, knn, alpha=0.4, top_n=100):
    title = search_movie(title_input, movie_meta)
    if not title:
        return ["Movie title not found."]
    return hybrid_recommendations_by_title(title, movie_meta, tfidf_matrix, user_movie_ratings, item_movie_matrix, knn, alpha, top_n)

# ✅ For precomputed recs (skips fuzzy search)
def hybrid_recommendations_by_title(title, movie_meta, tfidf_matrix, user_movie_ratings, item_movie_matrix, knn, alpha=0.4, top_n=20):
    if title not in movie_meta['title'].values:
        return ["Movie title not found."]

    idx = movie_meta[movie_meta['title'] == title].index[0]
    movie_id = movie_meta.loc[idx, 'movieId']

    content_sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    top_content_indices = np.argpartition(-content_sim, top_n)[:top_n]

    movie_idx_cf = user_movie_ratings.columns.get_loc(movie_id)
    movie_vector = item_movie_matrix.values[movie_idx_cf].reshape(1, -1)
    distances, indices_cf = knn.kneighbors(movie_vector, n_neighbors=top_n + 1)

    cf_scores = np.zeros_like(content_sim)
    for i, cf_idx in enumerate(indices_cf.flatten()[1:]):
        sim = 1 - distances.flatten()[i + 1]
        cf_scores[cf_idx] = sim

    content_sim /= content_sim.max()
    cf_scores /= cf_scores.max() if cf_scores.max() != 0 else 1
    hybrid_score = alpha * cf_scores + (1 - alpha) * content_sim
    hybrid_score[idx] = -1

    relevant_indices = np.union1d(top_content_indices, indices_cf.flatten()[1:])
    top_hybrid_indices = relevant_indices[np.argsort(hybrid_score[relevant_indices])[::-1][:top_n]]

    return movie_meta['title'].iloc[top_hybrid_indices[:top_n]].tolist()

def get_recommendations_from_db(movie_title, db_path="data/recommendations.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT recommendations FROM recommendations WHERE movie_title = ?", (movie_title,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return row[0].split('|')
        return []
    except Exception as e:
        print(f"Error fetching from DB: {e}")
        return []

