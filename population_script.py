import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WAD2_TEAM5A_PROJECT.settings')
django.setup()

import requests
import environ
import random
from datetime import datetime
from django.utils.timezone import make_aware, timezone
from django.utils import timezone as otimezone
from django.contrib.auth.models import User
from ScreenCritic.models import UserProfile, Media, Review, UserMediaSubscription, Genre, ReviewLike, UserFavouriteGenre

env = environ.Env()
environ.Env.read_env()

TMDB_API_KEY = env("TMDB_API_KEY")
RAWG_API_KEY = env("RAWG_API_KEY")

TMDB_BASE_URL = "https://api.themoviedb.org/3/discover"
RAWG_BASE_URL = "https://api.rawg.io/api/games"

def fetch_paginated_data(url, type_label, total_needed=200, max_per_page=20):
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
        if show.get('name') and show.get('first_air_date') and show.get('poster_path'):
            try:
                if Media.objects.filter(title=show['name'], type='TV Show').exists(): #check if media already exists
                    continue

                show_details = requests.get(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_API_KEY}").json() #get creator information
                creators = [person['name'] for person in show_details.get('created_by', [])]
                creator_str = ', '.join(creators) if creators else 'Unknown'
                
                tmdb_rating = show_details.get('vote_average', 0)
                normalised_rating = round((tmdb_rating / 10) * 5)  # Convert from 0-10 to 1-5 scale
                
                media = Media.objects.create(
                    title=show['name'],
                    type='TV Show',
                    description=show.get('overview', ''),
                    cover_image=f"https://image.tmdb.org/t/p/original{show['poster_path']}",
                    release_date=make_aware(datetime.strptime(show['first_air_date'], '%Y-%m-%d')),
                    creator=creator_str
                )

                genre_names = [genre["name"] for genre in show_details.get("genres", [])]
                genres = Genre.objects.filter(name__in=genre_names)
                media.genres.set(genres)
                
                create_reviews_for_media(media, normalised_rating)
                print(f"Created TV Show: {media.title} with rating: {normalised_rating}")
            except Exception as e:
                print(f"Failed to create TV Show {show.get('name')}: {str(e)}")

def fetch_movies(url, type_label):
    movies = fetch_paginated_data(url, type_label) #get a list of movie dicts

    for movie in movies:
        if movie.get('title') and movie.get('release_date') and movie.get('poster_path'):
            try:
                if Media.objects.filter(title=movie['title'], type='Movie').exists(): #check if media already exists
                    continue

                details_response = requests.get(f"https://api.themoviedb.org/3/movie/{movie['id']}?api_key={TMDB_API_KEY}") #make a request for the specific movie so we can get duration
                runtime = None
                if details_response.status_code == 200:
                    details = details_response.json()
                    runtime = details.get("runtime")
                    genre_names = [genre["name"] for genre in details.get("genres", [])]

                    tmdb_rating = details.get('vote_average', 0)
                    normalised_rating = round((tmdb_rating / 10) * 5)  #convert from 0-10 to 1-5 scale

                credits_response = requests.get(f"https://api.themoviedb.org/3/movie/{movie['id']}/credits?api_key={TMDB_API_KEY}") #make a request for the specific movie so we can get creator
                director_str = 'Unknown'
                if credits_response.status_code == 200:
                    credits_data = credits_response.json()
                    crew = credits_data.get('crew', [])
                    directors = [person['name'] for person in crew if person['job'] == 'Director']
                    director_str = ', '.join(directors) if directors else 'Unknown'
                
                media = Media.objects.create(
                    title=movie['title'],
                    type='Movie',
                    description=movie.get('overview', ''),
                    cover_image=f"https://image.tmdb.org/t/p/original{movie['poster_path']}",
                    duration=runtime,
                    release_date=make_aware(datetime.strptime(movie['release_date'], '%Y-%m-%d')),
                    creator=director_str
                )

                genres = Genre.objects.filter(name__in=genre_names)
                media.genres.set(genres)

                create_reviews_for_media(media, normalised_rating)
                print(f"Created Movie: {media.title} with rating: {normalised_rating}")
            except Exception as e:
                print(f"Failed to create Movie {movie.get('title')}: {str(e)}")

def fetch_games(url, type_label):
    games = fetch_paginated_data(url, type_label) #get a list of game dicts
    excluded_esrb_ratings = ['Adults Only', 'Mature']
    excluded_tags = ['nsfw', 'nudity', 'sexual content', 'erotic', 'adult', 'pegi 18', '18+']

    for game in games:
        if game.get('name') and game.get('released') and game.get('background_image'):
            esrb = game.get('esrb_rating')
            if esrb and esrb.get('name') in excluded_esrb_ratings:
                continue  #skip ESRB 18+ game

            #check for NSFW or PEGI-related tags
            tags = [tag['name'].lower() for tag in game.get('tags', [])]
            if any(bad_tag in tags for bad_tag in excluded_tags):
                continue  #skip NSFW or PEGI-18 style game

            try:
                if Media.objects.filter(title=game['name'], type='Game').exists(): #check if media already exists
                    continue

                details_response = requests.get(f"https://api.rawg.io/api/games/{game['id']}?key={RAWG_API_KEY}") #make a request for the specific game so we can get description
                description = None
                developer_str = 'Unknown'
                genre_names = []
                if details_response.status_code == 200:
                    details = details_response.json()
                    description = details.get("description")
                    genre_names = [genre["name"] for genre in details.get("genres", [])]
                    developers = [dev['name'] for dev in details.get('developers', [])]
                    developer_str = ', '.join(developers) if developers else 'Unknown'

                    rawg_rating = details.get('rating', 0)
                    if rawg_rating is None or rawg_rating == 0:
                        normalised_rating = 0
                    else:
                        normalised_rating = max(1, min(5, round(rawg_rating)))
                
                media = Media.objects.create(
                    title=game['name'],
                    type='Game',
                    description=description,
                    cover_image=game['background_image'],
                    release_date=make_aware(datetime.strptime(game['released'], '%Y-%m-%d')),
                    creator=developer_str
                )

                genres = Genre.objects.filter(name__in=genre_names)
                media.genres.set(genres)
                
                create_reviews_for_media(media, normalised_rating)
                print(f"Created Game: {media.title} with rating: {normalised_rating}")
            except Exception as e:
                print(f"Failed to create Game {game.get('name')}: {str(e)}")

def create_reviews_for_media(media, base_rating):
    users = list(User.objects.all())
    num_reviews = random.randint(5, 10) #random number of reviews between 5 and 10
    media_reviewers = random.sample(users, num_reviews) #random users to review the media
    
    review_texts = [
        "Absolutely loved it! A masterpiece that exceeded all expectations.",
        "One of the best experiences I've had, highly recommend!",
        "Outstanding performance by the creator(s)!",
        "Really impressed with the attention to detail.",
        "A must-see/play/watch for fans of the genre!",
        "Decent entertainment, but nothing groundbreaking.",
        "Solid entertainment from start to finish.",
        "Worth checking out if you're a fan of similar works.",
        "Surprisingly good, went in with low expectations.",
        "Could have been better, but still enjoyable.",
        "Had potential but fell short in execution.",
        "Interesting concept but could have been better executed.",
        "Not my cup of tea, but I can see why others might enjoy it.",
        "A bit disappointing considering the hype.",
        "Mixed feelings about this one."
    ]

    for user in media_reviewers:
        random_factor = random.gauss(0, 0.75)  #standard deviation of 0.75 for more variation
        rating = round(base_rating + random_factor)
        
        rating = max(1, min(5, rating)) #ensure rating stays within 1-5 range
        
        #select review text based on rating
        if rating >= 4: 
            review_text = random.choice(review_texts[0:5])  #positive reviews
        elif rating == 3:
            review_text = random.choice(review_texts[5:10])  #neutral reviews
        else:
            review_text = random.choice(review_texts[10:15])  #negative reviews

        review = Review.objects.create(
            user=user,
            media=media,
            review=review_text,
            rating=rating
        )

        num_likes = random.randint(0, 10) #random number of likes for each review (between 0 and 10)
        liking_users = random.sample(users, num_likes) #get random users to like this review

        for liker in liking_users:
            ReviewLike.objects.get_or_create(user=liker, review=review)

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

def create_subscriptions():
    print("Creating Media Subscriptions...")
    users = User.objects.all()
    released_media = Media.objects.filter(release_date__lte=otimezone.now())
    
    for user in users:
        selected_media = random.sample(list(released_media), 4)
        for media in selected_media:
            UserMediaSubscription.objects.get_or_create(
                user=user,
                media=media,
                defaults={
                    'is_released': True,
                    'read_by_user': random.choice([True, False, False]),
                    'notification_date': media.release_date
                }
            )
        print(f"Created 4 subscriptions for user {user.username}")

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
    fetch_tv_shows(f"{TMDB_BASE_URL}/tv?api_key={TMDB_API_KEY}&sort_by=popularity.desc&with_original_language=ko", "TV Shows")
    fetch_movies(f"{TMDB_BASE_URL}/movie?api_key={TMDB_API_KEY}&sort_by=popularity.desc&primary_release_date.lte=2024-12-31", "Past Movies")
    fetch_movies(f"{TMDB_BASE_URL}/movie?api_key={TMDB_API_KEY}&sort_by=popularity.desc&primary_release_year=2025", "Upcoming Movies")
    fetch_games(f"{RAWG_BASE_URL}?key={RAWG_API_KEY}&ordering=-released&dates=2000-01-01,2024-12-31", "Past Games")
    fetch_games(f"{RAWG_BASE_URL}?key={RAWG_API_KEY}&ordering=-added&dates=2025-01-01,2025-12-31", "Upcoming Games")
    create_subscriptions()
    create_user_favorite_genres()
    print("Database Populated Successfully!")
