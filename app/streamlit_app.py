import streamlit as st
st.set_page_config(page_title="Movie Recommender", layout="wide")

import pandas as pd
from data_loader import load_movie_meta, load_tfidf_matrix
from rec_engine import hybrid_recommendations
import requests
from PIL import Image
from io import BytesIO
from sklearn.neighbors import NearestNeighbors
from scipy import sparse

# --- Build KNN from saved sparse matrix ---
@st.cache_resource
def build_knn():
    item_matrix = sparse.load_npz("data/item_movie_matrix.npz")
    knn_model = NearestNeighbors(metric="cosine", algorithm="brute")
    knn_model.fit(item_matrix)
    return knn_model, item_matrix

# --- Safe image rendering ---
def safe_image_display(url):
    try:
        if not url or not isinstance(url, str) or url.strip() == "":
            raise ValueError("Invalid URL")
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content))
        st.image(img, use_container_width=True)
        return True
    except:
        # Display blank space same height as image
        st.markdown("""
            <div style='height:600px; background-color:#eee; border:1px solid #ccc;'></div>
        """, unsafe_allow_html=True)
        return False

# --- Load data ---
movie_meta = load_movie_meta()
tfidf_matrix = load_tfidf_matrix()
knn, item_movie_matrix = build_knn()

# --- App Layout ---
st.title("Movie Recommendation System")

if 'recommendations' not in st.session_state:
    st.subheader("Tell us what you like")

    # Genre selection
    st.markdown("### Pick at least one genre (you can select more):")
    genres_list = sorted(set("|".join(movie_meta['genres'].dropna()).split('|')))
    selected_genres = st.multiselect("Select genres", genres_list)

    # Movie preference
    st.markdown("### Pick movies you enjoy (up to 10):")
    all_titles = movie_meta['title'].dropna().unique().tolist()
    selected_movie = st.selectbox("Pick one movie you enjoy", ["" ] + all_titles)
    selected_movies = [selected_movie] if selected_movie else []

    if len(selected_movies) > 0 and st.button("Get Recommendations"):
        st.session_state['recommendations'] = hybrid_recommendations(
            selected_genres, selected_movies, tfidf_matrix, movie_meta
        )
        st.session_state['selected_movies'] = selected_movies
        st.rerun()

    st.stop()

# --- Show Recommendations ---
st.subheader("Recommended for you:")

recs = st.session_state['recommendations']
cols = st.columns(3)

for idx, movie in enumerate(recs[:9]):
    col = cols[idx % 3]
    with col:
        movie_info = movie_meta[movie_meta['title'] == movie]
        if movie_info.empty:
            continue
        movie_info = movie_info.iloc[0]

        with st.container():
            safe_image_display(movie_info.get('poster_url', ''))

            st.markdown(f"**{movie}**")
            meta_str = f"{movie_info['genres']} | {movie_info['director']} | {movie_info['age_rating'] or 'N/A'}"
            st.caption(meta_str)

            if movie_info['description']:
                with st.expander("Description"):
                    st.write(movie_info['description'])

# --- Reset Button ---
st.markdown("---")
if st.button("Try Again"):
    for key in ['recommendations', 'selected_movies']:
        st.session_state.pop(key, None)
    st.rerun()

