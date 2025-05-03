import streamlit as st
import pandas as pd
import numpy as np
from rec_engine import hybrid_recommendations
import joblib

# Load preprocessed data
movie_meta = pd.read_csv('data/movie_meta.csv')  # groupby movieId + combined_features
tfidf_matrix = joblib.load('data/tfidf_matrix.pkl')
user_movie_ratings = joblib.load('data/user_movie_ratings.pkl')
item_movie_matrix = joblib.load('data/item_movie_matrix.pkl')
knn = joblib.load('data/knn_model.pkl')

st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title("🎬 Movie Recommendation System (Session-Based)")

# Step 1: Cold Start Questions
if 'preferences' not in st.session_state:
    st.subheader("👋 Let's get to know your taste")
    fav_genre = st.text_input("Enter your favorite genre (e.g., Action, Comedy)")
    fav_movie = st.text_input("Enter a favorite movie you like")
    if st.button("Submit"):
        st.session_state['preferences'] = {
            'genre': fav_genre,
            'movie': fav_movie,
            'watched': [],
            'disliked': []
        }
        st.rerun()
    st.stop()

# Step 2: Generate initial recommendations
if 'recommendations' not in st.session_state:
    initial_movie = st.session_state['preferences']['movie']
    recs = hybrid_recommendations(initial_movie, movie_meta, tfidf_matrix,
                                  user_movie_ratings, item_movie_matrix, knn)
    st.session_state['recommendations'] = recs

# Step 3: Display 3x3 Grid
st.subheader("🎥 Recommended Movies for You")
cols = st.columns(3)

for i, movie in enumerate(st.session_state['recommendations'][:9]):
    col = cols[i % 3]
    with col:
        movie_info = movie_meta[movie_meta['title'] == movie].iloc[0]
        if movie_info['poster_url']:
            st.image(movie_info['poster_url'], use_column_width=True)
        st.markdown(f"**{movie}**")
        col1, col2 = st.columns(2)
        if col1.button("✅ Watched", key=f"watched_{i}"):
            st.session_state['preferences']['watched'].append(movie)
            new_recs = hybrid_recommendations(
                movie, movie_meta, tfidf_matrix, user_movie_ratings, item_movie_matrix, knn)
            for rec in new_recs:
                if rec not in st.session_state['recommendations']:
                    st.session_state['recommendations'][i] = rec
                    break
            st.rerun()
        if col2.button("👎 Bad Rating", key=f"bad_{i}"):
            st.session_state['preferences']['disliked'].append(movie)
            new_recs = hybrid_recommendations(
                movie, movie_meta, tfidf_matrix, user_movie_ratings, item_movie_matrix, knn)
            for rec in new_recs:
                if rec not in st.session_state['recommendations']:
                    st.session_state['recommendations'][i] = rec
                    break
            st.rerun()

