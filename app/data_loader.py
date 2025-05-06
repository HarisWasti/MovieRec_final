import pandas as pd
from scipy import sparse
import streamlit as st

@st.cache_resource
def load_movie_meta():
    return pd.read_parquet("data/movie_meta.parquet")

@st.cache_resource
def load_tfidf_matrix():
    return sparse.load_npz("data/tfidf_matrix.npz")

@st.cache_resource
def load_item_movie_matrix():
    return sparse.load_npz("data/item_movie_matrix.npz")
