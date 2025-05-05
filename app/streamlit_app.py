import streamlit as st
import pandas as pd
from data_loader import load_movie_meta, load_tfidf_matrix
from rec_engine import cold_start_recommendations
import requests
from PIL import Image
from io import BytesIO

def safe_image_display(url):
    try:
        if not url or not isinstance(url, str) or url.strip() == "":
            return False
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content))
        st.image(img, use_container_width=True)
        return True
    except:
        return False

# Load data
movie_meta = load_movie_meta()
tfidf_matrix = load_tfidf_matrix()

st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("Movie Recommendation System")

# Step 1: Input genre and movie preferences
if 'recommendations' not in st.session_state:
    st.subheader("Tell us what you like")

    # Genre selection
    st.markdown("### Pick at least one genre (you can select more):")
    genres_list = sorted(set("|".join(movie_meta['genres'].dropna()).split('|')))
    selected_genres = st.multiselect("Select genres", genres_list)

    # Movie search with autocomplete
    st.markdown("### Pick movies you enjoy (up to 10):")
    all_titles = movie_meta['title'].dropna().unique().tolist()
    selected_movies = []
    for i in range(1, 11):
        movie = st.selectbox(f"Pick movie {i}", [""] + all_titles, key=f"movie_{i}")
        if movie and movie not in selected_movies:
            selected_movies.append(movie)

    if len(selected_movies) > 0 and st.button("Get Recommendations"):
        st.session_state['recommendations'] = cold_start_recommendations(selected_genres, selected_movies, tfidf_matrix, movie_meta)
        st.session_state['selected_movies'] = selected_movies
        st.rerun()
    st.stop()

# Step 2: Show Recommendations
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

        image_height = 625
        with st.container():
            if not safe_image_display(movie_info.get('poster_url', '')):
                st.markdown(
                    f'<div style="height:{image_height}px; display:flex; align-items:center; justify-content:center; background-color:#eee; border:1px solid #ccc;">'
                    'Poster unavailable</div>',
                    unsafe_allow_html=True
                )

            st.markdown(f"**{movie}**")
            meta_str = f"{movie_info['genres']} | {movie_info['director']} | {movie_info['age_rating'] or 'N/A'}"
            st.caption(meta_str)

            if movie_info['description']:
                with st.expander("Description"):
                    st.write(movie_info['description'])

# Reset option
st.markdown("---")
if st.button("Try Again"):
    for key in ['recommendations', 'selected_movies']:
        st.session_state.pop(key, None)
    st.rerun()

