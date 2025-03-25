from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Avg
from ScreenCritic.models import Media, Review, ReviewLike, UserFavouriteGenre
from django.urls import reverse

# Create your views here.
def home(request):
    return render(request, 'ScreenCritic/index.html')

def movie_list(request):
    movies = Media.objects.filter(type='Movie').order_by('-release_date')

    suggested_movies = []
    if request.user.is_authenticated:
        favorite_genres = UserFavouriteGenre.objects.filter(user=request.user).values_list('genre', flat=True)
        if favorite_genres.exists():
            suggested_movies = Media.objects.filter(type='Movie', genres__in=favorite_genres).annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    trending_movies = (Media.objects.filter(type='Movie').annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]) #get recommended media (other media of same type)
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

def tv_list(request):

    shows = Media.objects.filter(type='TV Show', slug__isnull=False, slug__gt='').order_by('-release_date')

    suggested_shows = []
    if request.user.is_authenticated:
        favorite_genres = UserFavouriteGenre.objects.filter(user=request.user).values_list('genre', flat=True)
        if favorite_genres.exists():
            suggested_shows = Media.objects.filter(type='TV Show', genres__in=favorite_genres, slug__isnull=False, slug__gt='').annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    trending_shows = (Media.objects.filter(type='TV Show', slug__isnull=False, slug__gt='').annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]) #get recommended media (other media of same type)
    shows_alphabetically = (Media.objects.filter(type='TV Show', slug__isnull=False, slug__gt='').order_by('title'))

    shows_by_genre = {}

    for show in Media.objects.filter(type='TV Show', slug__isnull=False, slug__gt='').prefetch_related('genres'):
        for genre in show.genres.all():
            if genre.name not in shows_by_genre:
                shows_by_genre[genre.name] = []
            shows_by_genre[genre.name].append(show)

    context = {
        'media_list': shows,
        'media_type': 'TV Shows',
        'trending_movies': trending_shows,
        'movies_alphabetically': shows_alphabetically,
        'movies_by_genre': shows_by_genre,
        'suggested_movies': suggested_shows,
    }

    return render(request, 'ScreenCritic/media.html', context)

def game_list(request):
    games = Media.objects.filter(type='Game').order_by('-release_date')

    suggested_games = []
    if request.user.is_authenticated:
        favorite_genres = UserFavouriteGenre.objects.filter(user=request.user).values_list('genre', flat=True)
        if favorite_genres.exists():
            suggested_games = Media.objects.filter(type='Game', genres__in=favorite_genres).annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    trending_games = (Media.objects.filter(type='Game').annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]) #get recommended media (other media of same type)
    games_alphabetically = (Media.objects.filter(type='Game').order_by('title'))

    games_by_genre = {}

    for game in Media.objects.filter(type='Game').prefetch_related('genres'):
        for genre in game.genres.all():
            if genre.name not in games_by_genre:
                games_by_genre[genre.name] = []
            games_by_genre[genre.name].append(game)

    context = {
        'media_list': games,
        'media_type': 'Games',
        'trending_movies': trending_games,
        'movies_alphabetically': games_alphabetically,
        'movies_by_genre': games_by_genre,
        'suggested_movies': suggested_games,
        
    }

    return render(request, 'ScreenCritic/media.html', context)

def media_detail(request, slug, media_type):
    media = get_object_or_404(Media, slug=slug, type=media_type) #get the media object with the slug and media type

    sort_by = request.GET.get('sort', 'default')

    reviews = (Review.objects.filter(media=media).annotate(likes_count=Count('reviewlike')).order_by('-likes_count', '-date')) #get all reviews for this media

    if sort_by == 'likes': #most liked first
        reviews = reviews.order_by('-likes_count', '-date')
    elif sort_by == 'username': #alphabetical by username
        reviews = reviews.order_by('user__username', '-date')
    elif sort_by == 'recent': #most recent first
        reviews = reviews.order_by('-date')
    elif sort_by == 'rating': #highest rating first
        reviews = reviews.order_by('-rating', '-date')
    else:  #default is most liked
        reviews = reviews.order_by('-likes_count', '-date')

    #get the total ratings and average rating stats
    rating_stats = reviews.aggregate(
        total_ratings=Count('rating'),
        average_rating=Avg('rating')
    )
    total_ratings = rating_stats['total_ratings'] or 0
    average_rating = rating_stats['average_rating'] or 0
    text_reviews_count = reviews.exclude(review__isnull=True).exclude(review__exact='').count()

    recommended_media = (Media.objects.filter(type=media_type).exclude(slug=slug).annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]) #get recommended media (other media of same type)

    if request.user.is_authenticated:
        liked_reviews = set(ReviewLike.objects.filter(user=request.user).values_list('review_id', flat=True))
    else:
        liked_reviews = set()

    context = {
        'media': media,
        'reviews': reviews,
        'recommended_media': recommended_media,
        'total_ratings': total_ratings,
        'average_rating': average_rating,
        'text_reviews_count': text_reviews_count,
        'current_sort': sort_by,
        'liked_reviews': liked_reviews
    }

    return render(request, 'ScreenCritic/title.html', context)

def like_review(request, review_id):
    if not request.user.is_authenticated: #redirect to login page if not authenticated
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)

    review = Review.objects.get(pk=review_id) #get the review object
    liked, created = ReviewLike.objects.get_or_create(user=request.user, review=review) #get or create the review like object

    if not created: #if the review like object already exists, delete it as it is being unliked
        liked.delete()
        liked_status = False
    else: #if the review like object does not exist, create it as it is being liked
        liked_status = True

    like_count = ReviewLike.objects.filter(review=review).count() #get the number of likes for the review
    return JsonResponse({'likes': like_count, 'liked': liked_status}) #return the number of likes and the liked status