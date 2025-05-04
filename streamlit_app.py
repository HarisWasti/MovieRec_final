import streamlit as st
import pandas as pd
import requests
from data_loader import load_all_data
from rec_engine import get_recommendations_from_db

# Set up Streamlit page
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 Movie Recommendation System")

# Load required data
data = load_all_data()
movie_meta = data["movie_meta"]

# Session State Initialization
st.session_state.setdefault('preferences', {})
st.session_state.setdefault('recommendations', [])

# Step 1: Ask for movie only
if 'movie' not in st.session_state['preferences']:
    st.subheader("👋 What's one movie you liked?")

    search_input = st.text_input("🔍 Type a movie title")
    movie_options = movie_meta['title'].dropna().unique().tolist()
    matched_movies = [m for m in movie_options if search_input.lower() in m.lower()]

    if matched_movies:
        for m in matched_movies[:10]:  # Show top 10 buttons
            if st.button(m):
                st.session_state['preferences'] = {'movie': m}
                st.session_state['recommendations'] = get_recommendations_from_db(m)
                st.rerun()
    elif search_input:
        st.warning("❌ No matching movie found.")
    st.stop()

# Step 2: Show 4x5 Grid of Recommendations
recs = st.session_state['recommendations']

if not recs:
    st.error("No recommendations found.")
    st.stop()

st.subheader(f"🎥 Because you liked **{st.session_state['preferences']['movie']}**...")

cols = st.columns(4)
for idx, movie in enumerate(recs[:20]):
    col = cols[idx % 4]
    with col:
        movie_info = movie_meta[movie_meta['title'] == movie]
        if movie_info.empty:
            continue
        movie_info = movie_info.iloc[0]

        poster_url = movie_info.get("poster_url", None)
        if poster_url:
            try:
                response = requests.get(poster_url)
                if response.status_code == 200:
                    st.image(poster_url, use_container_width=True)
                else:
                    st.markdown("🖼️ *No poster*")
            except:
                st.markdown("🖼️ *No poster*")
        else:
            st.markdown("🖼️ *No poster*")

        st.markdown(f"**{movie}**")
        st.caption(f"🎬 {movie_info['genres']} | 👨‍🎓 {movie_info['director']} | 🔞 {movie_info['age_rating'] or 'N/A'}")

        if movie_info['description']:
            with st.expander("🛈 Description"):
                st.write(movie_info['description'])

# Try again
st.markdown("---")
if st.button("🔁 Try Again with Different Movie"):
    for key in ['preferences', 'recommendations']:
        st.session_state.pop(key, None)
    st.rerun()
