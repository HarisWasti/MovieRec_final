# rec_engine.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def search_movie(title_input, movie_meta):
    title_input = title_input.lower()
    filtered = movie_meta[movie_meta['title'].str.lower().str.contains(title_input, regex=False)]
    return filtered['title'].iloc[0] if not filtered.empty else None

def hybrid_recommendations(title_input, movie_meta, tfidf_matrix, user_movie_ratings, item_movie_matrix, knn, alpha=0.4):
    title = search_movie(title_input, movie_meta)
    if not title:
        return ["Movie title not found."]

    idx = movie_meta[movie_meta['title'] == title].index[0]
    movie_id = movie_meta.loc[idx, 'movieId']

    content_sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    movie_idx_cf = user_movie_ratings.columns.get_loc(movie_id)
    movie_vector = item_movie_matrix.values[movie_idx_cf].reshape(1, -1)
    distances, indices_cf = knn.kneighbors(movie_vector, n_neighbors=11)

    cf_scores = np.zeros_like(content_sim)
    for i, cf_idx in enumerate(indices_cf.flatten()[1:]):
        sim = 1 - distances.flatten()[i + 1]
        cf_scores[cf_idx] = sim

    content_sim /= content_sim.max()
    cf_scores /= cf_scores.max() if cf_scores.max() != 0 else 1
    hybrid_score = alpha * cf_scores + (1 - alpha) * content_sim
    hybrid_score[idx] = -1

    similar_indices = hybrid_score.argsort()[::-1][:10]
    return movie_meta['title'].iloc[similar_indices].tolist()
