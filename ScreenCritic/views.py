from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Avg
from django.urls import reverse

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import UserProfile, Review, Media, Genre, UserFavouriteGenre, ReviewLike
from .forms import LoginForm, ProfileEditForm, RegisterForm, ReviewForm

from .templatetags.custom_filters import route_name


# Create your views here.
def home(request): #render the home page
    return render(request, 'ScreenCritic/base.html')

def movie_list(request): #display list of movies with sorting and filtering options
    movies = Media.objects.filter(type='Movie').order_by('-release_date') #get all movies ordered by release date
    suggested_movies = []
    if request.user.is_authenticated: #if user is logged in, get personalised suggestions
        favorite_genres = UserFavouriteGenre.objects.filter(user=request.user).values_list('genre', flat=True)
        if favorite_genres.exists():
            suggested_movies = Media.objects.filter(
                type='Movie',
                genres__in=favorite_genres
            ).annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    trending_movies = Media.objects.filter(type='Movie').annotate(
        avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20] #get top 20 movies by rating
    movies_alphabetically = Media.objects.filter(type='Movie').order_by('title') #get movies in alphabetical order
    movies_by_genre = {}

    for movie in Media.objects.filter(type='Movie').prefetch_related('genres'): #organise movies by genre
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

def tv_list(request): #display list of TV shows with sorting and filtering options
    shows = Media.objects.filter(type='TV Show', slug__isnull=False, slug__gt='').order_by('-release_date') #get all TV shows ordered by release date
    suggested_shows = []
    if request.user.is_authenticated: #if user is logged in, get personalised suggestions
        favorite_genres = UserFavouriteGenre.objects.filter(user=request.user).values_list('genre', flat=True)
        if favorite_genres.exists():
            suggested_shows = Media.objects.filter(
                type='TV Show',
                genres__in=favorite_genres,
                slug__isnull=False,
                slug__gt=''
            ).annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    trending_shows = Media.objects.filter(type='TV Show', slug__isnull=False, slug__gt='').annotate(
        avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20] #get top 20 shows by rating
    shows_alphabetically = Media.objects.filter(type='TV Show', slug__isnull=False, slug__gt='').order_by('title') #get shows in alphabetical order
    shows_by_genre = {}

    for show in Media.objects.filter(type='TV Show', slug__isnull=False, slug__gt='').prefetch_related('genres'): #organise shows by genre
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

def game_list(request): #display list of games with sorting and filtering options
    games = Media.objects.filter(type='Game').order_by('-release_date') #get all games ordered by release date
    suggested_games = []
    if request.user.is_authenticated: #if user is logged in, get personalised suggestions
        favorite_genres = UserFavouriteGenre.objects.filter(user=request.user).values_list('genre', flat=True)
        if favorite_genres.exists():
            suggested_games = Media.objects.filter(
                type='Game',
                genres__in=favorite_genres
            ).annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20]

    trending_games = Media.objects.filter(type='Game').annotate(
        avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20] #get top 20 games by rating
    games_alphabetically = Media.objects.filter(type='Game').order_by('title') #get games in alphabetical order
    games_by_genre = {}

    for game in Media.objects.filter(type='Game').prefetch_related('genres'): #organise games by genre
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

def media_detail(request, slug, media_type): #display detailed information about a specific media item
    media = get_object_or_404(Media, slug=slug, type=media_type) #get media object or return 404
    sort_by = request.GET.get('sort', 'default') #get sort parameter from URL

    reviews = Review.objects.filter(media=media).annotate(
        likes_count=Count('reviewlike')).order_by('-likes_count', '-date') #get reviews with like count

    if sort_by == 'likes': #sort reviews by number of likes
        reviews = reviews.order_by('-likes_count', '-date')
    elif sort_by == 'username': #sort reviews by username
        reviews = reviews.order_by('user__username', '-date')
    elif sort_by == 'recent': #sort reviews by date
        reviews = reviews.order_by('-date')
    elif sort_by == 'rating': #sort reviews by rating
        reviews = reviews.order_by('-rating', '-date')

    rating_stats = reviews.aggregate(total_ratings=Count('rating'), average_rating=Avg('rating')) #calculate rating statistics
    total_ratings = rating_stats['total_ratings'] or 0
    average_rating = rating_stats['average_rating'] or 0
    text_reviews_count = reviews.exclude(review__isnull=True).exclude(review__exact='').count() #count text reviews

    recommended_media = Media.objects.filter(type=media_type).exclude(slug=slug).annotate(
        avg_rating=Avg('review__rating')).order_by('-avg_rating')[:20] #get recommended media items

    liked_reviews = set() #initialize set for liked reviews
    if request.user.is_authenticated: #if user is logged in, get their liked reviews
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

def like_review(request, review_id): #handle review likes
    if not request.user.is_authenticated: #check if user is logged in
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method != 'POST': #check if request method is POST
        return JsonResponse({'error': 'Invalid method'}, status=400)

    review = Review.objects.get(pk=review_id) #get review object
    liked, created = ReviewLike.objects.get_or_create(user=request.user, review=review) #create or get like

    if not created: #if like already exists, remove it
        liked.delete()
        liked_status = False
    else: #if like was created, set status to True
        liked_status = True

    like_count = ReviewLike.objects.filter(review=review).count() #get the number of likes for the review
    return JsonResponse({'likes': like_count, 'liked': liked_status}) #return the number of likes and the liked status

def media_review(request, slug, media_type=None): #handle media review submission
    if not media_type: #if media type not provided, get it from media object
        media = get_object_or_404(Media, slug=slug)
        media_type = media.type
    else:
        media = get_object_or_404(Media, slug=slug, type=media_type)
    
    if not request.user.is_authenticated: #check if user is logged in
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
    if request.method == 'POST': #handle form submission
        form_type = request.POST.get('form_type')
        
        # Handle login
        if form_type == 'login': #process login form
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
        
        # Handle registration
        elif form_type == 'register': #process registration form
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if User.objects.filter(username=username).exists(): #check if username exists
                messages.error(request, "Username already exists")
                return redirect('ScreenCritic:login_register')
            
            if User.objects.filter(email=email).exists(): #check if email exists
                messages.error(request, "Email already in use")
                return redirect('ScreenCritic:login_register')
            
            if password1 != password2: #check if passwords match
                messages.error(request, "Passwords don't match")
                return redirect('ScreenCritic:login_register')
            
            try:
                user = User.objects.create_user(username=username, email=email, password=password1) #create user
                UserProfile.objects.create(user=user, email=email) #create user profile
                login(request, user)
                messages.success(request, "Account created successfully!")
                return redirect('ScreenCritic:profile')
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
                return redirect('ScreenCritic:login_register')

    # For GET requests, still provide the forms for template rendering
    login_form = LoginForm() #create login form
    register_form = RegisterForm() #create registration form
    
    context = {
        'login_form': login_form,
        'register_form': register_form
    }
    return render(request, 'ScreenCritic/login_register.html', context)

def user_logout(request): #handle user logout
    logout(request) #log out the user
    return redirect(reverse('ScreenCritic:home')) #redirect to homepage

@login_required
def profile_view(request): #display user profile
    user_profile = UserProfile.objects.filter(user=request.user).first() #get user profile
    favorite_genres = UserFavouriteGenre.objects.filter(user=request.user) #get favorite genres
    active_tab = request.GET.get("tab", "reviewed") #get active tab from URL
    sort_option = request.GET.get("sort", "rating-desc") #get sort option from URL

    if sort_option == "rating-asc": #set sort field based on option
        order_by_field = "rating"
    elif sort_option == "date-desc":
        order_by_field = "-date"
    elif sort_option == "date-asc":
        order_by_field = "date"
    else:
        order_by_field = "-rating"

    context = {
        "user_profile": user_profile,
        "favorite_genres": favorite_genres,
        "active_tab": active_tab,
        "current_sort": sort_option,
    }

    if active_tab == "to-review": #handle to-review tab
        user_genres = [fav.genre for fav in favorite_genres]
        to_review_media = Media.objects.filter(genres__in=user_genres).distinct().exclude(review__user=request.user)
        context["to_review_media"] = to_review_media
    elif active_tab == "liked": #handle liked tab
        liked_reviews = Review.objects.filter(reviewlike__user=request.user).order_by(order_by_field)
        liked_review_ids = ReviewLike.objects.filter(user=request.user).values_list('review_id', flat=True)
        context["liked_reviews"] = liked_reviews
        context["liked_review_ids"] = list(liked_review_ids)
    else: #handle reviewed tab
        reviewed_reviews = Review.objects.filter(user=request.user).order_by(order_by_field)
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
            form.save() #save form data
            if "delete_picture" in request.POST and user_profile.profile_picture: #handle profile picture deletion
                user_profile.profile_picture.delete(save=False)
                user_profile.profile_picture = None
                user_profile.save()

            selected_genres = request.POST.getlist("favorite_genres") #get selected genres
            removed_genres_str = request.POST.get("removed_genres", "") #get removed genres
            if removed_genres_str: #handle removed genres
                removed_ids = removed_genres_str.split(",")
                UserFavouriteGenre.objects.filter(user=request.user, genre__genre_id__in=removed_ids).delete()

            for genre_id in selected_genres: #handle selected genres
                genre_obj, _ = Genre.objects.get_or_create(genre_id=genre_id)
                UserFavouriteGenre.objects.get_or_create(user=request.user, genre=genre_obj)

            return redirect("ScreenCritic:profile")
    else:
        form = ProfileEditForm(instance=user_profile) #create form instance

    return render(request, "ScreenCritic/edit_profile.html", {
        "form": form,
        "user_profile": user_profile,
        "genres": genres,
        "user_favorite_genres": user_favorite_genres,
    })