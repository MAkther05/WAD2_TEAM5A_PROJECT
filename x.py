import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WAD2_TEAM5A_PROJECT.settings')
django.setup()

import requests
import environ
import random
from datetime import datetime
from django.utils.timezone import make_aware
from django.contrib.auth.models import User
from ScreenCritic.models import UserProfile, Media, Review, UserMediaSubscription, Genre, ReviewLike, UserFavouriteGenre

env = environ.Env()
environ.Env.read_env()

TMDB_API_KEY = env("TMDB_API_KEY")
RAWG_API_KEY = env("RAWG_API_KEY")

movie_id = 550  # Example: Fight Club

# Step 1: Fetch movie details
movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
movie_response = requests.get(movie_url)
if movie_response.status_code == 200:
    movie_data = movie_response.json()
    print(f"Movie Title: {movie_data.get('title')}")
    print("Director (from movie details): Not available here\n")
else:
    print("Failed to fetch movie details")

# Step 2: Fetch credits to get the director
credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}"
credits_response = requests.get(credits_url)
if credits_response.status_code == 200:
    credits_data = credits_response.json()
    crew = credits_data.get('crew', [])
    directors = [person['name'] for person in crew if person['job'] == 'Director']
    print(f"Director(s) from credits: {', '.join(directors) if directors else 'No Director Found'}")
else:
    print("Failed to fetch movie credits")
