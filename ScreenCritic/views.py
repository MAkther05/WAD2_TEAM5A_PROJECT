from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Avg
from ScreenCritic.models import Media, Review, ReviewLike, UserFavouriteGenre


def home(request):
    return render(request, 'ScreenCritic/index.html')


def tv_list(request):
    shows = Media.objects.filter(type='TV Show').order_by('-release_date')

    suggested_shows = []
    if request.user.is_authenticated:
        favorite_genres = UserFavouriteGenre.objects.filter(user=request.user).values_list('genre', flat=True)
        if favorite_genres.exists():
            suggested_shows = Media.objects.filter(type='TV Show', genres__in=favorite_genres).distinct()[:10]

    trending_shows = Media.objects.filter(type='TV Show').annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]
    shows_alphabetically = Media.objects.filter(type='TV Show').order_by('title')

    context = {
        'media_list': shows,
        'media_type': 'TV Shows',
        'trending_media': trending_shows,
        'media_alphabetically': shows_alphabetically,
        'suggested_media': suggested_shows,
    }
    return render(request, 'ScreenCritic/media.html', context)


def movie_list(request):
    movies = Media.objects.filter(type='Movie').order_by('-release_date')

    suggested_movies = []
    if request.user.is_authenticated:
        favorite_genres = UserFavouriteGenre.objects.filter(user=request.user).values_list('genre', flat=True)
        if favorite_genres.exists():
            suggested_movies = Media.objects.filter(type='Movie', genres__in=favorite_genres).distinct()[:10]

    trending_movies = Media.objects.filter(type='Movie').annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]
    movies_alphabetically = Media.objects.filter(type='Movie').order_by('title')

    context = {
        'media_list': movies,
        'media_type': 'Movies',
        'trending_media': trending_movies,
        'media_alphabetically': movies_alphabetically,
        'suggested_media': suggested_movies,
    }
    return render(request, 'ScreenCritic/media.html', context)


def game_list(request):
    games = Media.objects.filter(type='Game').order_by('-release_date')

    suggested_games = []
    if request.user.is_authenticated:
        favorite_genres = UserFavouriteGenre.objects.filter(user=request.user).values_list('genre', flat=True)
        if favorite_genres.exists():
            suggested_games = Media.objects.filter(type='Game', genres__in=favorite_genres).distinct()[:10]

    trending_games = Media.objects.filter(type='Game').annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]
    games_alphabetically = Media.objects.filter(type='Game').order_by('title')

    context = {
        'media_list': games,
        'media_type': 'Games',
        'trending_media': trending_games,
        'media_alphabetically': games_alphabetically,
        'suggested_media': suggested_games,
    }
    return render(request, 'ScreenCritic/media.html', context)
