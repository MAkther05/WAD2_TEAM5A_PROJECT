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

TMDB_BASE_URL = "https://api.themoviedb.org/3/discover"
RAWG_BASE_URL = "https://api.rawg.io/api/games"

def fetch_paginated_data(url, type_label, total_needed=100, max_per_page=20):
    print(f"Fetching {total_needed} {type_label} from API...")

    results = []
    page = 1

    while len(results) < total_needed: #loops until 100 media has been fetched
        response = requests.get(f"{url}&page={page}") #makes api request for each page required
        
        if response.status_code == 200: #if request is successful
            data = response.json().get("results", []) #sets data as 'results' which is a list of dicts of the data either that or an empty list if 'results' not in response.json
            results.extend(data) #adds the list of data to the total list of data
            
            print(f"Fetched {len(results)} / {total_needed} {type_label} so far...")

            if len(data) < max_per_page:  #if the page has less than 20 data then it's the last page so should break from the loop and return the current list
                break

        else:
            print(f"Failed to fetch page {page} for {type_label}.")
            break

        page += 1

    return results[:total_needed]

def fetch_tv_shows(url, type_label):
    tv_shows = fetch_paginated_data(url, type_label) #get a list of tv show dicts

    for show in tv_shows:
        media, _ = Media.objects.get_or_create(
            title=show["name"],
            type="TV Show",
            description=show.get("overview"),
            cover_image=f"https://image.tmdb.org/t/p/original{show['poster_path']}" if show.get("poster_path") else None,
            duration=None, #no duration as episodes may be inconsistent length
            release_date=make_aware(datetime.strptime(show["first_air_date"], "%Y-%m-%d")) if show.get("first_air_date") else None
        )

        genre_names = [genre["name"] for genre in show.get("genres", [])]
        genres = Genre.objects.filter(name__in=genre_names)
        media.genres.set(genres)

        print(f"Created TV Show: {show['name']}")

def fetch_movies(url, type_label):
    movies = fetch_paginated_data(url, type_label) #get a list of movie dicts

    for movie in movies:
        details_response = requests.get(f"https://api.themoviedb.org/3/movie/{movie['id']}?api_key={TMDB_API_KEY}") #make a request for the specific movie so we can get duration
        runtime = None
        if details_response.status_code == 200:
            details = details_response.json()
            runtime = details.get("runtime")
            genre_names = [genre["name"] for genre in details.get("genres", [])]

        media, _ = Media.objects.get_or_create(
            title=movie["title"],
            type="Movie",
            description=movie.get("overview"),
            cover_image=f"https://image.tmdb.org/t/p/original{movie['poster_path']}" if movie.get("poster_path") else None,
            duration=runtime,
            release_date=make_aware(datetime.strptime(movie["release_date"], "%Y-%m-%d")) if movie.get("release_date") else None
        )

        genres = Genre.objects.filter(name__in=genre_names)
        media.genres.set(genres)

        print(f"Created Movie: {movie['title']}")

def fetch_games(url, type_label):
    games = fetch_paginated_data(url, type_label) #get a list of game dicts

    for game in games:
        details_response = requests.get(f"https://api.rawg.io/api/games/{game['id']}?key={RAWG_API_KEY}") #make a request for the specific game so we can get description
        description = None
        genre_names = []
        if details_response.status_code == 200:
            details = details_response.json()
            description = details.get("description")
            genre_names = [genre["name"] for genre in details.get("genres", [])]

        media, _ = Media.objects.get_or_create(
            title=game["name"],
            type="Game",
            description=description,
            cover_image=game["background_image"] if game.get("background_image") else None,
            duration=None, #games don’t have durations
            release_date=make_aware(datetime.strptime(game["released"], "%Y-%m-%d")) if game.get("released") else None
        )

        genres = Genre.objects.filter(name__in=genre_names)
        media.genres.set(genres)

        print(f"Created Game: {game['name']}")

def create_users():
    print("Creating 50 Users...")
    first_names = ["John", "Alice", "Michael", "Emma", "Robert", "Sophia", "James", "Isabella", "William", "Olivia",
                   "David", "Charlotte", "Daniel", "Amelia", "Matthew", "Mia", "Joseph", "Evelyn", "Samuel", "Harper"]

    last_names = ["Smith", "Johnson", "Brown", "Williams", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

    usernames = set() #set for unique usernames

    while len(usernames) < 50: #creates 50 random users using the names above and a randomly generated number
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        number = random.randint(1, 99)

        username = f"{first_name}{last_name}{number}"

        if username not in usernames:
            usernames.add(username)

            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, email=f"{username}@example.com", password="password123")
                UserProfile.objects.create(user=user, email=user.email)
                print(f"Created User: {username}")

def create_reviews():
    print("Creating Reviews...")
    users = list(User.objects.all())
    media_items = list(Media.objects.all())

    for _ in range(100):  #creates 100 random reviews
        user = random.choice(users)
        media = random.choice(media_items)
        rating = random.randint(1, 5)
        review_text = f"This is a review for {media.title} by {user.username}."

        Review.objects.create(
            user=user,
            media=media,
            review=review_text,
            rating=rating
        )

    print("Reviews Created.")

def create_review_likes():
    print("Creating Review Likes...")

    users = list(User.objects.all())
    reviews = list(Review.objects.all())

    for _ in range(200):  #200 random likes
        user = random.choice(users)
        review = random.choice(reviews)
        ReviewLike.objects.get_or_create(user=user, review=review)

    print("Review Likes Created.")

def create_subscriptions():
    print("Creating Subscriptions...")
    users = list(User.objects.all())
    media_items = list(Media.objects.all())

    for _ in range(100):  #creates 100 random subscriptions
        user = random.choice(users)
        media = random.choice(media_items)
        UserMediaSubscription.objects.get_or_create(user=user, media=media)

    print("Subscriptions Created.")

def fetch_tmdb_genres():
    print("Fetching Movie/TV Genres from TMDB...")
    
    response = requests.get(f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}")
    if response.status_code == 200:
        genres = response.json()["genres"]

        for genre in genres:
            Genre.objects.get_or_create(name=genre["name"])

    print("Created Movie/TV Genres from TMDB.")

def fetch_rawg_genres():
    print("Fetching Game Genres from RAWG...")

    response = requests.get(f"https://api.rawg.io/api/genres?key={RAWG_API_KEY}")
    if response.status_code == 200:
        genres = response.json()["results"]

        for genre in genres:
            Genre.objects.get_or_create(name=genre["name"])

    print("Created Game Genres from RAWG.")

def create_user_favorite_genres():
    print("Creating User Favorite Genres...")

    users = list(User.objects.all())
    genres = list(Genre.objects.all())

    for user in users: #gives every user 3 random favourite genres
        favorite_genres = random.sample(genres, k=random.randint(1, 3))
        for genre in favorite_genres:
            UserFavouriteGenre.objects.get_or_create(user=user, genre=genre)

    print("User Favorite Genres Created.")

if __name__ == "__main__":
    create_users()
    fetch_tmdb_genres()
    fetch_rawg_genres()
    fetch_tv_shows(f"{TMDB_BASE_URL}/tv?api_key={TMDB_API_KEY}&sort_by=popularity.desc&first_air_date.lte=2024-12-31", "Past TV Shows")
    fetch_tv_shows(f"{TMDB_BASE_URL}/tv?api_key={TMDB_API_KEY}&sort_by=popularity.desc&first_air_date.gte=2025-01-01&first_air_date.lte=2025-12-31", "Upcoming TV Shows")
    fetch_movies(f"{TMDB_BASE_URL}/movie?api_key={TMDB_API_KEY}&sort_by=popularity.desc&primary_release_date.lte=2024-12-31", "Past Movies")
    fetch_movies(f"{TMDB_BASE_URL}/movie?api_key={TMDB_API_KEY}&sort_by=popularity.desc&primary_release_year=2025", "Upcoming Movies")
    fetch_games(f"{RAWG_BASE_URL}?key={RAWG_API_KEY}&ordering=-released&dates=2000-01-01,2024-12-31", "Past Games")
    fetch_games(f"{RAWG_BASE_URL}?key={RAWG_API_KEY}&ordering=-added&dates=2025-01-01,2025-12-31", "Upcoming Games")
    create_reviews()
    create_subscriptions()
    create_review_likes()
    create_user_favorite_genres()
    print("Database Populated Successfully!")
