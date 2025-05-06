import streamlit as st
import sqlite3
import pandas as pd
from data_loader import load_movie_meta
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Movie Recommender", layout="wide")

# --- Load data ---
movie_meta = load_movie_meta()
DB_PATH = "data/recommendations.db"

# --- Image Display ---
def safe_image_display(url):
    try:
        if not url or not isinstance(url, str) or url.strip() == "":
            raise ValueError("Invalid URL")
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content))
        st.image(img, use_container_width=True)
        return True
    except:
        st.markdown("""
            <div style='height:600px; background-color:#eee; border:1px solid #ccc;'></div>
        """, unsafe_allow_html=True)
        return False

# --- App Layout ---
st.title("Movie Recommendation System")

if 'recommendations' not in st.session_state:
    st.subheader("Tell us what you like")

    all_titles = movie_meta['title'].dropna().unique().tolist()
    selected_movie = st.selectbox("Pick one movie you enjoy", [""] + all_titles)

    if selected_movie and st.button("Get Recommendations"):
        with sqlite3.connect(DB_PATH) as conn:
            query = "SELECT recommendations FROM recommendations WHERE movie_title = ?"
            result = conn.execute(query, (selected_movie,)).fetchone()
        
        if result:
            recs = result[0].split('|')
            st.session_state['recommendations'] = recs
            st.session_state['selected_movie'] = selected_movie
            st.rerun()
        else:
            st.error("No recommendations found for this movie.")
    st.stop()

# --- Show Recommendations ---
st.subheader(f"Recommended for: {st.session_state['selected_movie']}")

recs = st.session_state['recommendations']
cols = st.columns(3)

for idx, movie in enumerate(recs[:9]):
    col = cols[idx % 3]
    with col:
        movie_info = movie_meta[movie_meta['title'] == movie]
        if movie_info.empty:
            continue
        movie_info = movie_info.iloc[0]

        safe_image_display(movie_info.get('poster_url', ''))
        st.markdown(f"**{movie}**")
        st.caption(f"{movie_info['genres']} | {movie_info['director']} | {movie_info.get('age_rating', 'N/A')}")

        if movie_info['description']:
            with st.expander("Description"):
                st.write(movie_info['description'])

# --- Reset Button ---
st.markdown("---")
if st.button("Try Again"):
    for key in ['recommendations', 'selected_movie']:
        st.session_state.pop(key, None)
    st.rerun()
