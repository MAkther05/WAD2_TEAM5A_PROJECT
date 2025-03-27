from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Avg

from ScreenCritic.forms import LoginForm, ProfileEditForm, RegisterForm, ReviewForm
from ScreenCritic.templatetags.custom_filters import route_name
from django.templatetags.static import static
from .models import UserProfile, Review, Media, Genre, UserFavouriteGenre, ReviewLike
from .forms import ProfileEditForm, UserDeleteForm
from .forms import LoginForm, ProfileEditForm, RegisterForm, ReviewForm

from .templatetags.custom_filters import route_name
from django.views.decorators.http import require_GET


def home(request):
    return render(request, 'ScreenCritic/base.html')


def movie_list(request):
    movies = Media.objects.filter(type='Movie').order_by('-release_date')
    suggested_movies = []
    if request.user.is_authenticated:
        favorite_genres = UserFavouriteGenre.objects.filter(user=request.user).values_list('genre', flat=True)
        if favorite_genres.exists():
            suggested_movies = Media.objects.filter(
                type='Movie',
                genres__in=favorite_genres
            ).annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    trending_movies = Media.objects.filter(type='Movie').annotate(
        avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]
    movies_alphabetically = Media.objects.filter(type='Movie').order_by('title')
    movies_by_genre = {}

    for movie in Media.objects.filter(type='Movie').prefetch_related('genres'):
        for genre in movie.genres.all():
            movies_by_genre.setdefault(genre.name, []).append(movie)

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
            suggested_shows = Media.objects.filter(
                type='TV Show',
                genres__in=favorite_genres,
                slug__isnull=False,
                slug__gt=''
            ).annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    trending_shows = Media.objects.filter(type='TV Show', slug__isnull=False, slug__gt='').annotate(
        avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]
    shows_alphabetically = Media.objects.filter(type='TV Show', slug__isnull=False, slug__gt='').order_by('title')
    shows_by_genre = {}

    for show in Media.objects.filter(type='TV Show', slug__isnull=False, slug__gt='').prefetch_related('genres'):
        for genre in show.genres.all():
            shows_by_genre.setdefault(genre.name, []).append(show)

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
            suggested_games = Media.objects.filter(
                type='Game',
                genres__in=favorite_genres
            ).annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    trending_games = Media.objects.filter(type='Game').annotate(
        avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]
    games_alphabetically = Media.objects.filter(type='Game').order_by('title')
    games_by_genre = {}

    for game in Media.objects.filter(type='Game').prefetch_related('genres'):
        for genre in game.genres.all():
            games_by_genre.setdefault(genre.name, []).append(game)

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
    media = get_object_or_404(Media, slug=slug, type=media_type)
    sort_by = request.GET.get('sort', 'default')

    reviews = Review.objects.filter(media=media).annotate(
        likes_count=Count('reviewlike')).order_by('-likes_count', '-date')

    if sort_by == 'likes':
        reviews = reviews.order_by('-likes_count', '-date')
    elif sort_by == 'username':
        reviews = reviews.order_by('user__username', '-date')
    elif sort_by == 'recent':
        reviews = reviews.order_by('-date')
    elif sort_by == 'rating':
        reviews = reviews.order_by('-rating', '-date')

    rating_stats = reviews.aggregate(total_ratings=Count('rating'), average_rating=Avg('rating'))
    total_ratings = rating_stats['total_ratings'] or 0
    average_rating = rating_stats['average_rating'] or 0
    text_reviews_count = reviews.exclude(review__isnull=True).exclude(review__exact='').count()

    recommended_media = Media.objects.filter(type=media_type).exclude(slug=slug).annotate(
        avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    liked_reviews = set()
    if request.user.is_authenticated:
        liked_reviews = set(ReviewLike.objects.filter(user=request.user).values_list('review_id', flat=True))

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
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)

    review = Review.objects.get(pk=review_id)
    liked, created = ReviewLike.objects.get_or_create(user=request.user, review=review)

    if not created:
        liked.delete()
        liked_status = False
    else:
        liked_status = True

    like_count = ReviewLike.objects.filter(review=review).count()
    return JsonResponse({'likes': like_count, 'liked': liked_status})


def media_review(request, slug, media_type=None):
    if not media_type:
        media = get_object_or_404(Media, slug=slug)
        media_type = media.type
    else:
        media = get_object_or_404(Media, slug=slug, type=media_type)

    if not request.user.is_authenticated:
        messages.error(request, "You need to login to submit a review.")
        return redirect('ScreenCritic:login_register')

    if Review.objects.filter(user=request.user, media=media).exists():
        messages.warning(request, "You've already reviewed this media.")
        return redirect(route_name(media_type), slug=slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.media = media
            review.save()
            return redirect(route_name(media_type), slug=slug)
    else:
        form = ReviewForm()

    return render(request, 'ScreenCritic/write_review.html', {'form': form, 'media': media})


def login_register(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Logged in successfully!")
                return redirect('ScreenCritic:home')
            else:
                messages.error(request, "Invalid username or password")
                return redirect('ScreenCritic:login_register')

        elif form_type == 'register':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
                return redirect('ScreenCritic:login_register')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already in use")
                return redirect('ScreenCritic:login_register')

            if password1 != password2:
                messages.error(request, "Passwords don't match")
                return redirect('ScreenCritic:login_register')

            try:
                user = User.objects.create_user(username=username, email=email, password=password1)
                UserProfile.objects.create(user=user, email=email)
                login(request, user)
                messages.success(request, "Account created successfully!")
                return redirect('ScreenCritic:profile')
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
                return redirect('ScreenCritic:login_register')

    login_form = LoginForm()
    register_form = RegisterForm()

    context = {
        'login_form': login_form,
        'register_form': register_form
    }
    return render(request, 'ScreenCritic/login_register.html', context)


def user_logout(request):
    logout(request)
    return redirect(reverse('ScreenCritic:home'))


@login_required
def profile_view(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    user_profile = UserProfile.objects.filter(user=user).first()
    favorite_genres = UserFavouriteGenre.objects.filter(user=user)
    active_tab = request.GET.get("tab", "reviewed")
    sort_option = request.GET.get("sort", "rating-desc")

    if sort_option == "rating-asc":
        order_by_field = "rating"
    elif sort_option == "date-desc":
        order_by_field = "-date"
    elif sort_option == "date-asc":
        order_by_field = "date"
    else:
        order_by_field = "-rating"

    liked_review_ids = list(ReviewLike.objects.filter(user=request.user).values_list('review_id', flat=True))

    context = {
        "user_profile": user_profile,
        "favorite_genres": favorite_genres,
        "active_tab": active_tab,
        "current_sort": sort_option,
        "liked_reviews_ids": liked_review_ids,
    }

    if active_tab == "to-review":
        user_genres = [fav.genre for fav in favorite_genres]
        to_review_media = Media.objects.filter(genres__in=user_genres).distinct().exclude(review__user=user)
        context["to_review_media"] = to_review_media
    elif active_tab == "liked":
        liked_reviews = Review.objects.filter(reviewlike__user=user).order_by(order_by_field)
        context["liked_reviews"] = liked_reviews
    else:
        reviewed_reviews = Review.objects.filter(user=user).order_by(order_by_field)
        context["reviewed_reviews"] = reviewed_reviews

    return render(request, "ScreenCritic/profile.html", context)


@login_required
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    genres = Genre.objects.values("genre_id", "name")
    user_favorite_genres = UserFavouriteGenre.objects.filter(user=request.user)

    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            if "delete_picture" in request.POST and user_profile.profile_picture:
                user_profile.profile_picture.delete(save=False)
                user_profile.profile_picture = None
                user_profile.save()

            selected_genres = request.POST.getlist("favorite_genres")
            removed_genres_str = request.POST.get("removed_genres", "")
            if removed_genres_str:
                removed_ids = removed_genres_str.split(",")
                UserFavouriteGenre.objects.filter(user=request.user, genre__genre_id__in=removed_ids).delete()

            for genre_id in selected_genres:
                genre_obj, _ = Genre.objects.get_or_create(genre_id=genre_id)
                UserFavouriteGenre.objects.get_or_create(user=request.user, genre=genre_obj)

            return redirect("ScreenCritic:profile")
    else:
        form = ProfileEditForm(instance=user_profile)

    return render(request, "ScreenCritic/edit_profile.html", {
        "form": form,
        "user_profile": user_profile,
        "genres": genres,
        "user_favorite_genres": user_favorite_genres,
    })


@login_required
def deleteuser(request):
    if request.method == 'POST':
        delete_form = UserDeleteForm(request.POST, instance=request.user)
        user = request.user
        user.delete()
        messages.info(request, 'Your account has been deleted.')
        return redirect('ScreenCritic:home')
    else:
        delete_form = UserDeleteForm(instance=request.user)

    context = {
        'delete_form': delete_form
    }

    return render(request, 'ScreenCritic/delete_account.html', context)

@require_GET
def live_search(request):
    query = request.GET.get('q', '')

    user_matches = UserProfile.objects.filter(user__username__icontains=query)[:5]
    media_matches = Media.objects.filter(title__icontains=query)[:5]

    def resolve_image(value, fallback):
        if not value:
            return fallback
        value = str(value)
        if value.startswith('http'):
            return value
        if hasattr(value, 'url'):
            return value.url
        return fallback

    results = {
        'users': [
            {
                'username': u.user.username,
                'profile_picture': resolve_image(u.profile_picture, '/static/images/default_profile.png')
            }
            for u in user_matches
        ],
        'media': [
            {
                'title': m.title,
                'slug': m.slug,
                'type': m.type,
                'cover_image': resolve_image(m.cover_image, '/static/images/logo.png')
            }
            for m in media_matches
        ]
    }

    return JsonResponse(results)
