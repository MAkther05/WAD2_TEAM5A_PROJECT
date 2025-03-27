<<<<<<< HEAD
=======
from django.contrib.auth import authenticate, login, logout
>>>>>>> main
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.timezone import now
<<<<<<< HEAD

=======
from django.db.models import Avg, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.http import require_GET

from .forms import (
    LoginForm,
    ProfileEditForm,
    RegisterForm,
    ReviewForm,
    UserDeleteForm
)
from .models import (
    Genre,
    Media, 
    Review,
    ReviewLike,
    UserFavouriteGenre,
    UserProfile
)
>>>>>>> main
from .templatetags.custom_filters import route_name

def home(request):

    top_rated_media = Media.objects.annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:5]

    upcoming_media = Media.objects.filter(release_date__gt=now()).annotate(
        avg_rating=Avg('review__rating')).order_by('-avg_rating')[:10]

    trending_movies = Media.objects.filter(type='Movie').annotate(
        avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    trending_shows = Media.objects.filter(type='TV Show', slug__isnull=False, slug__gt='').annotate(
        avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    trending_games = Media.objects.filter(type='Game').annotate(
        avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    context = {
        'trending_movies': trending_movies,
        'trending_shows': trending_shows,
        'trending_games': trending_games,
        'upcoming_media': upcoming_media,
        'top_rated_media': top_rated_media

    }

    return render(request, 'ScreenCritic/index.html', context)

<<<<<<< HEAD
=======
def home(request): #render the home page
    return render(request, 'ScreenCritic/base.html')
>>>>>>> main

def movie_list(request): #display list of movies and related movie content
    movies = Media.objects.filter(type='Movie').order_by('-release_date') #get all movies ordered by release date
    suggested_movies = []
    if request.user.is_authenticated:
        favorite_genres = UserFavouriteGenre.objects.filter(user=request.user).values_list('genre', flat=True) #get user's favorite genres
        if favorite_genres.exists():
            suggested_movies = Media.objects.filter( #get suggested movies based on user's favorite genres
                type='Movie',
                genres__in=favorite_genres
            ).annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    trending_movies = Media.objects.filter(type='Movie').annotate( #get trending movies based on ratings
        avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]
    movies_alphabetically = Media.objects.filter(type='Movie').order_by('title') #get movies sorted alphabetically
    movies_by_genre = {} #organize movies by genre

    for movie in Media.objects.filter(type='Movie').prefetch_related('genres'): #group movies by their genres
        for genre in movie.genres.all():
            movies_by_genre.setdefault(genre.name, []).append(movie)

    context = { #prepare context data for template
        'media_list': movies,
        'media_type': 'Movies',
        'trending_movies': trending_movies,
        'movies_alphabetically': movies_alphabetically,
        'movies_by_genre': movies_by_genre,
        'suggested_movies': suggested_movies,
    }
    return render(request, 'ScreenCritic/media.html', context)

def tv_list(request): #display list of TV shows and related TV content
    shows = Media.objects.filter(type='TV Show', slug__isnull=False, slug__gt='').order_by('-release_date') #get all TV shows ordered by release date
    suggested_shows = []
    if request.user.is_authenticated:
        favorite_genres = UserFavouriteGenre.objects.filter(user=request.user).values_list('genre', flat=True) #get user's favorite genres
        if favorite_genres.exists():
            suggested_shows = Media.objects.filter( #get suggested shows based on user's favorite genres
                type='TV Show',
                genres__in=favorite_genres,
                slug__isnull=False,
                slug__gt=''
            ).annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    trending_shows = Media.objects.filter(type='TV Show', slug__isnull=False, slug__gt='').annotate( #get trending shows based on ratings
        avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]
    shows_alphabetically = Media.objects.filter(type='TV Show', slug__isnull=False, slug__gt='').order_by('title') #get shows sorted alphabetically
    shows_by_genre = {} #organize shows by genre

    for show in Media.objects.filter(type='TV Show', slug__isnull=False, slug__gt='').prefetch_related('genres'): #group shows by their genres
        for genre in show.genres.all():
            shows_by_genre.setdefault(genre.name, []).append(show)

    context = { #prepare context data for template
        'media_list': shows,
        'media_type': 'TV Shows',
        'trending_movies': trending_shows,
        'movies_alphabetically': shows_alphabetically,
        'movies_by_genre': shows_by_genre,
        'suggested_movies': suggested_shows,
    }
    return render(request, 'ScreenCritic/media.html', context)

def game_list(request): #display list of games and related game content
    games = Media.objects.filter(type='Game').order_by('-release_date') #get all games ordered by release date
    suggested_games = []
    if request.user.is_authenticated:
        favorite_genres = UserFavouriteGenre.objects.filter(user=request.user).values_list('genre', flat=True) #get user's favorite genres
        if favorite_genres.exists():
            suggested_games = Media.objects.filter( #get suggested games based on user's favorite genres
                type='Game',
                genres__in=favorite_genres
            ).annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    trending_games = Media.objects.filter(type='Game').annotate( #get trending games based on ratings
        avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]
    games_alphabetically = Media.objects.filter(type='Game').order_by('title') #get games sorted alphabetically
    games_by_genre = {} #organize games by genre

    for game in Media.objects.filter(type='Game').prefetch_related('genres'): #group games by their genres
        for genre in game.genres.all():
            games_by_genre.setdefault(genre.name, []).append(game)

    context = { #prepare context data for template
        'media_list': games,
        'media_type': 'Games',
        'trending_movies': trending_games,
        'movies_alphabetically': games_alphabetically,
        'movies_by_genre': games_by_genre,
        'suggested_movies': suggested_games,
    }
    return render(request, 'ScreenCritic/media.html', context)

def media_detail(request, slug, media_type): #display detailed view of a specific media item
    media = get_object_or_404(Media, slug=slug, type=media_type) #get media object or return 404
    sort_by = request.GET.get('sort', 'default') #get sort parameter from request

    reviews = Review.objects.filter(media=media).annotate( #get reviews for the media
        likes_count=Count('reviewlike')).order_by('-likes_count', '-date')

    if sort_by == 'likes': #sort reviews based on user preference
        reviews = reviews.order_by('-likes_count', '-date')
    elif sort_by == 'username':
        reviews = reviews.order_by('user__username', '-date')
    elif sort_by == 'recent':
        reviews = reviews.order_by('-date')
    elif sort_by == 'rating':
        reviews = reviews.order_by('-rating', '-date')

    rating_stats = reviews.aggregate(total_ratings=Count('rating'), average_rating=Avg('rating')) #calculate rating statistics
    total_ratings = rating_stats['total_ratings'] or 0
    average_rating = rating_stats['average_rating'] or 0
    text_reviews_count = reviews.exclude(review__isnull=True).exclude(review__exact='').count()

    recommended_media = Media.objects.filter(type=media_type).exclude(slug=slug).annotate( #get recommended media
        avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    liked_reviews = set()
    if request.user.is_authenticated: #get user's liked reviews if authenticated
        liked_reviews = set(ReviewLike.objects.filter(user=request.user).values_list('review_id', flat=True))

    context = { #prepare context data for template
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

def like_review(request, review_id): #handle review like/unlike functionality
    if not request.user.is_authenticated: #check if user is authenticated
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method != 'POST': #validate request method
        return JsonResponse({'error': 'Invalid method'}, status=400)

    review = Review.objects.get(pk=review_id) #get review object
    liked, created = ReviewLike.objects.get_or_create(user=request.user, review=review) #create or get like object

    if not created: #toggle like status
        liked.delete()
        liked_status = False
    else:
        liked_status = True

    like_count = ReviewLike.objects.filter(review=review).count() #get updated like count
    return JsonResponse({'likes': like_count, 'liked': liked_status})

def media_review(request, slug, media_type=None): #handle media review submission
    if not media_type: #get media object based on type
        media = get_object_or_404(Media, slug=slug)
        media_type = media.type
    else:
        media = get_object_or_404(Media, slug=slug, type=media_type)

    if not request.user.is_authenticated: #check if user is authenticated
        return redirect(f"{reverse('ScreenCritic:login_register')}?next={request.path}")

    if Review.objects.filter(user=request.user, media=media).exists(): #check if user already reviewed
        return redirect(route_name(media_type), slug=slug)

    if request.method == 'POST': #handle form submission
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

def login_register(request): #handle user login and registration
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'login': #handle login form
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Logged in successfully!")
                return redirect('ScreenCritic:profile')
            else:
                messages.error(request, "Invalid username or password")
                return redirect('ScreenCritic:login_register')

        elif form_type == 'register': #handle registration form
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if User.objects.filter(username=username).exists(): #validate username
                messages.error(request, "Username already exists")
                return redirect('ScreenCritic:login_register')

            if User.objects.filter(email=email).exists(): #validate email
                messages.error(request, "Email already in use")
                return redirect('ScreenCritic:login_register')

            if password1 != password2: #validate passwords match
                messages.error(request, "Passwords don't match")
                return redirect('ScreenCritic:login_register')

            try: #create new user
                user = User.objects.create_user(username=username, email=email, password=password1)
                UserProfile.objects.create(user=user, email=email)
                login(request, user)
                messages.success(request, "Account created successfully!")
                return redirect('ScreenCritic:profile')
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
                return redirect('ScreenCritic:login_register')

    login_form = LoginForm() #prepare forms for template
    register_form = RegisterForm()

    context = {
        'login_form': login_form,
        'register_form': register_form
    }
    return render(request, 'ScreenCritic/login_register.html', context)

def user_logout(request): #handle user logout
    logout(request)
    return redirect(reverse('ScreenCritic:home'))

@login_required
def profile_view(request, username=None): #display user profile
    if username: #get user object
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    user_profile = UserProfile.objects.filter(user=user).first() #get user profile
    favorite_genres = UserFavouriteGenre.objects.filter(user=user) #get user's favorite genres
    active_tab = request.GET.get("tab", "reviewed") #get active tab from request
    sort_option = request.GET.get("sort", "rating-desc") #get sort option from request

    if sort_option == "rating-asc": #determine sort order
        order_by_field = "rating"
    elif sort_option == "date-desc":
        order_by_field = "-date"
    elif sort_option == "date-asc":
        order_by_field = "date"
    else:
        order_by_field = "-rating"

    liked_review_ids = list(ReviewLike.objects.filter(user=request.user).values_list('review_id', flat=True)) #get user's liked reviews

    context = { #prepare initial context
        "user_profile": user_profile,
        "favorite_genres": favorite_genres,
        "active_tab": active_tab,
        "current_sort": sort_option,
        "liked_reviews_ids": liked_review_ids,
    }

    if active_tab == "to-review": #handle to-review tab
        user_genres = [fav.genre for fav in favorite_genres]
        to_review_media = Media.objects.filter(genres__in=user_genres).distinct().exclude(review__user=user)
        context["to_review_media"] = to_review_media
    elif active_tab == "liked": #handle liked tab
        liked_reviews = Review.objects.filter(reviewlike__user=user).order_by(order_by_field)
        context["liked_reviews"] = liked_reviews
    else: #handle reviewed tab
        reviewed_reviews = Review.objects.filter(user=user).order_by(order_by_field)
        context["reviewed_reviews"] = reviewed_reviews

    return render(request, "ScreenCritic/profile.html", context)

@login_required
def edit_profile(request): #handle profile editing
    user_profile = get_object_or_404(UserProfile, user=request.user) #get user profile
    genres = Genre.objects.values("genre_id", "name") #get all genres
    user_favorite_genres = UserFavouriteGenre.objects.filter(user=request.user) #get user's favorite genres

    if request.method == "POST": #handle form submission
        form = ProfileEditForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            if "delete_picture" in request.POST and user_profile.profile_picture: #handle profile picture deletion
                user_profile.profile_picture.delete(save=False)
                user_profile.profile_picture = None
                user_profile.save()

            selected_genres = request.POST.getlist("favorite_genres") #update favorite genres
            removed_genres_str = request.POST.get("removed_genres", "")
            if removed_genres_str:
                removed_ids = removed_genres_str.split(",")
                UserFavouriteGenre.objects.filter(user=request.user, genre__genre_id__in=removed_ids).delete()

            for genre_id in selected_genres: #add new favorite genres
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
def deleteuser(request): #handle user account deletion
    if request.method == 'POST': #process deletion request
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
def live_search(request): #handle live search functionality
    query = request.GET.get('q', '') #get search query

    if not query.strip(): #return empty results if query is empty or only whitespace
        return JsonResponse({
            'users': [],
            'media': []
        })

    user_matches = UserProfile.objects.filter(user__username__icontains=query)[:5] #search for users
    media_matches = Media.objects.filter(title__icontains=query)[:5] #search for media

    def resolve_image(value, fallback): #helper function to resolve image URLs
        if not value:
            return fallback
        value = str(value)
        if value.startswith('http'):
            return value
        if hasattr(value, 'url'):
            return value.url
        return fallback

    results = { #prepare search results
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
