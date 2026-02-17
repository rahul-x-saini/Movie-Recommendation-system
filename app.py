import pickle
import streamlit as st
import requests
import os
from dotenv import load_dotenv
import gdown

load_dotenv()  # Load variables from .env
API_KEY = os.getenv("TMDB_API_KEY")

# -----------------------------
# Step 1: Set up pickle files
# -----------------------------
files = {
    "similarity.pkl": "1jg3PjX6Z711an87fYcAynLZiTOotC0lc",
    "movielist.pkl": "1S_Mryz72uo7B_wAGvjVokabqk-lbyemv"
}

for fname, file_id in files.items():
    if not os.path.exists(fname):
        url = f"https://drive.google.com/uc?id={file_id}"
        st.write(f"Downloading {fname}...")
        gdown.download(url, fname, quiet=False)

# -----------------------------
# Step 2: Load pickle files
# -----------------------------
with open("similarity.pkl", "rb") as f:
    similarity = pickle.load(f)

with open("movielist.pkl", "rb") as f:
    movies = pickle.load(f)

# -----------------------------
# Step 3: Streamlit app
# -----------------------------

st.set_page_config(layout="wide", page_title="Movie Recommender", page_icon="🎬")

st.markdown("""
    <h1 style='text-align: center; color: #E50914;'>🎬 Movie Recommendation System</h1>
    <p style='text-align: center;'>Find movies similar to your favorites</p>
""", unsafe_allow_html=True)


movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)


@st.cache_data(ttl=3600)
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=1d0fdef8509641a14c2ae45e530425f9&language=en-US".format(movie_id)
    data = requests.get(url)
    if data.status_code == 200:
       data = data.json()
       return data
    else:
        st.error(f"Failed to fetch movie with ID {movie_id}")
        return []


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = []
    for i in distances[1:11]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_data = fetch_poster(movie_id)
        recommended_movies.append(fetch_poster(movie_id))

    return recommended_movies



if st.button('Show Recommendation'):
    recommended_movies_data = recommend(selected_movie)

    for i in range(0, 10, 5):
        cols = st.columns(5)
        for col, movie in zip(cols, recommended_movies_data[i:i + 5]):
            with col:
                poster_url = "https://image.tmdb.org/t/p/w500" + movie['poster_path']
                st.image(poster_url, use_container_width=True)
                st.caption(f"{movie['title']} ({movie['vote_average']:.1f}⭐)")


@st.cache_data(ttl=3600)
def fetch_trending():
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results']  # list of movies
    else:
        st.error("Failed to fetch trending movies")
        return []



st.subheader("🔥 Trending This Week")

trending_movies = fetch_trending()

# Show top 10 trending
top_trending = trending_movies[:10]

cols_per_row = 5

for i in range(0, len(top_trending), cols_per_row):
    cols = st.columns(cols_per_row)
    for col, movie in zip(cols, top_trending[i:i+cols_per_row]):
        with col:
            poster_url = "https://image.tmdb.org/t/p/w500" + movie['poster_path']
            st.image(poster_url, use_container_width=True)
            st.caption(f"{movie['title']} ({movie['vote_average']:.1f}⭐)")





