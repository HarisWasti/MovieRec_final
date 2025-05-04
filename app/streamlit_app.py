import streamlit as st
import pandas as pd
from data_loader import load_movie_meta, get_recommendations_from_db

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

# Load metadata
movie_meta = load_movie_meta()

st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 Movie Recommendation System")

# Helper: Extract all genres
all_genres = sorted(set(g for genre_list in movie_meta['genres'].dropna() for g in genre_list.split('|')))

# Step 1: Cold Start Input
if 'preferences' not in st.session_state:
    st.subheader("👋 Start by selecting a movie you liked")

    # 🎯 Genre Selection (0 to 3)
    st.markdown("### 🎭 (Optional) Select up to 3 genres")
    selected_genres = st.multiselect("Pick up to 3 genres", all_genres, max_selections=3)

    # 🎬 Movie Selection (mandatory)
    st.markdown("### 🎬 Pick a movie you liked")
    movie_options = movie_meta['title'].dropna().unique().tolist()
    fav_movie = st.selectbox("Choose a movie", movie_options)

    # 🚀 Submit only if movie selected
    if fav_movie and st.button("Submit"):
        st.session_state['preferences'] = {
            'movie': fav_movie,
            'genres': selected_genres
        }
        st.session_state['recommendations'] = get_recommendations_from_db(fav_movie)
        st.rerun()
    st.stop()

# Step 2: Show Recommendations
st.subheader(f"🎥 Because you liked **{st.session_state['preferences']['movie']}**")

recs = st.session_state['recommendations']
cols = st.columns(4)

for idx, movie in enumerate(recs[:20]):
    col = cols[idx % 4]
    with col:
        movie_info = movie_meta[movie_meta['title'] == movie]
        if movie_info.empty:
            continue
        movie_info = movie_info.iloc[0]

        image_height = 530

        with st.container():
            if not safe_image_display(movie_info['poster_url']):
                st.markdown(
                    f'<div style="height:{image_height}px; display:flex; align-items:center; justify-content:center; background-color:#eee; border:1px solid #ccc;">'
                    '🖼️ <i>Poster unavailable</i></div>',
                    unsafe_allow_html=True
                )

            # ✅ Show title and metadata always
            st.markdown(f"**{movie}**")
            meta_str = f"🎬 {movie_info['genres']} | 👨‍🎓 {movie_info['director']} | 🔞 {movie_info['age_rating'] or 'N/A'}"
            st.caption(meta_str)

            if movie_info['description']:
                with st.expander("🛈 Description"):
                    st.write(movie_info['description'])


# Option to restart
st.markdown("---")
if st.button("🔁 Try Again"):
    for key in ['preferences', 'recommendations']:
        st.session_state.pop(key, None)
    st.rerun()
