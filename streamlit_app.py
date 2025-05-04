from rec_engine import get_recommendations_from_db 
import streamlit as st
import pandas as pd
import numpy as np
import requests
from rec_engine import hybrid_recommendations
import joblib
from scipy import sparse
from data_loader import load_all_data
from rec_engine import hybrid_recommendations

# 🔧 Session-safe init (✅ Add this early!)
st.set_page_config(page_title="Movie Recommender", layout="wide")

# Initialize session state keys to prevent KeyErrors
st.session_state.setdefault('preferences', {
    'genre': [],
    'movie': '',
    'watched': [],
    'rec_index': 9
})
st.session_state.setdefault('recommendations', [])

# Load all model/data files
data = load_all_data()
movie_meta = data["movie_meta"]
tfidf_matrix = data["tfidf_matrix"]
user_movie_ratings = data["user_movie_ratings"]
item_movie_matrix = data["item_movie_matrix"]
knn = data["knn"]

# Step 2: Generate recommendations only if 'preferences' exists
if st.session_state['preferences']['movie'] and not st.session_state['recommendations']:
    initial_movie = st.session_state['preferences']['movie']
    st.session_state['recommendations'] = get_recommendations_from_db(initial_movie)

# Step 3: Display 3x3 Grid of Recommendations
st.subheader("🎥 Recommended Movies for You")
cols = st.columns(3)
recs = st.session_state['recommendations']
rec_index = st.session_state['preferences']['rec_index']

# Edge case: user has watched all 20 recs
if rec_index >= len(recs):
    st.success("✅ You've seen all 20 recommendations!")
    if st.button("🔁 Try Again with Different Preferences"):
        for key in ['preferences', 'recommendations']:
            st.session_state.pop(key, None)
        st.rerun()
    st.stop()

# Show the first 9 recommendations
visible_recs = recs[:9]
for i, movie in enumerate(visible_recs):
    col = cols[i % 3]
    with col:
        movie_info = movie_meta[movie_meta['title'] == movie].iloc[0]
        with st.container():
            poster_url = movie_info['poster_url']
            if poster_url:
                try:
                    response = requests.get(poster_url)
                    if response.status_code == 200:
                        st.image(poster_url, use_container_width=True)
                    else:
                        st.markdown(
                            "<div style='height:300px; display:flex; align-items:center; justify-content:center; border:1px dashed #ccc;'>"
                            "🖼️ <em>No poster available</em></div>",
                            unsafe_allow_html=True
                        )
                except:
                    st.markdown(
                        "<div style='height:300px; display:flex; align-items:center; justify-content:center; border:1px dashed #ccc;'>"
                        "🖼️ <em>No poster available</em></div>",
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    "<div style='height:300px; display:flex; align-items:center; justify-content:center; border:1px dashed #ccc;'>"
                    "🖼️ <em>No poster available</em></div>",
                    unsafe_allow_html=True
                )

            st.markdown(f"**{movie}**")
            meta_str = f"🎬 {movie_info['genres']} | 👨‍🎓 {movie_info['director']} | 🔞 {movie_info['age_rating'] or 'N/A'}"
            st.caption(meta_str)

            if movie_info['description']:
                with st.expander("🛈 Description"):
                    st.write(movie_info['description'])

            if st.button("✅ Watched", key=f"watched_{i}"):
                st.session_state['preferences']['watched'].append(movie)

                recs = st.session_state['recommendations']
                rec_pointer = st.session_state['preferences']['rec_index']

                if rec_pointer < len(recs):
                    st.session_state['recommendations'][i] = recs[rec_pointer]
                    st.session_state['preferences']['rec_index'] += 1
                else:
                    st.session_state['recommendations'][i] = "No more recommendations"

                st.rerun()

# 🔁 Reset Option (bottom)
st.markdown("---")
if st.button("🔁 Try Again with Different Preferences"):
    for key in ['preferences', 'recommendations']:
        st.session_state.pop(key, None)
    st.rerun()
