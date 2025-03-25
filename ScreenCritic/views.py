from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Avg
from ScreenCritic.models import Media, Review, ReviewLike, UserFavouriteGenre

def home(request):
    return render(request, 'ScreenCritic/index.html')

def movie_list(request):
    movies = Media.objects.filter(type='Movie').order_by('-release_date')

    suggested_movies = []
    if request.user.is_authenticated:
        favorite_genres = UserFavouriteGenre.objects.filter(user=request.user).values_list('genre', flat=True)
        if favorite_genres.exists():
            suggested_movies = Media.objects.filter(genres__in=favorite_genres).distinct()[:10]

    trending_movies = (Media.objects.filter(type='Movie').annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20])
    movies_alphabetically = (Media.objects.filter(type='Movie').order_by('title'))

    movies_by_genre = {}

    for movie in Media.objects.filter(type='Movie').prefetch_related('genres'):
        for genre in movie.genres.all():
            if genre.name not in movies_by_genre:
                movies_by_genre[genre.name] = []
            movies_by_genre[genre.name].append(movie)

    context = {
        'media_list': movies,
        'media_type': 'Movies',
        'trending_movies': trending_movies,
        'movies_alphabetically': movies_alphabetically,
        'movies_by_genre': movies_by_genre,
        'suggested_movies': suggested_movies,
    }
    return render(request, 'ScreenCritic/media.html', context)
