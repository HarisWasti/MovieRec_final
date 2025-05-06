import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def cold_start_recommendations(fav_genres, fav_movies, tfidf_matrix, movie_meta, alpha=0.7, penalty_weight=0.2, k=9):
    genre_bonus = movie_meta['genres'].str.contains('|'.join(fav_genres), case=False, na=False).astype(float)

    scores = np.zeros(tfidf_matrix.shape[0])
    valid_titles = 0

    for title in fav_movies:
        match = movie_meta[movie_meta['title'].str.lower().str.contains(title.lower(), regex=False, na=False)]
        if not match.empty:
            idx = match.index[0]
            sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
            scores += sim
            valid_titles += 1

    if valid_titles == 0:
        return []

    scores /= valid_titles
    scores += 0.1 * genre_bonus.values

    # Apply popularity penalty
    if 'rating' in movie_meta.columns:
        popularity = movie_meta['rating'].fillna(0).values
        popularity = (popularity - popularity.min()) / (popularity.max() - popularity.min())
        scores -= penalty_weight * popularity

    # Remove the original movies from results
    fav_indices = movie_meta[movie_meta['title'].str.lower().isin([t.lower() for t in fav_movies])].index
    scores[fav_indices] = -1

    top_indices = scores.argsort()[::-1][:k]
    return movie_meta['title'].iloc[top_indices].tolist()

