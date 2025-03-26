from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Avg
from ScreenCritic.models import Media, Review, ReviewLike
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Review, Media, Genre, UserFavouriteGenre
from .forms import ProfileEditForm

# Create your views here.
def home(request):
    return render(request, 'ScreenCritic/base.html')

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

@login_required
def profile_view(request):
    user_profile = UserProfile.objects.filter(user=request.user).first()
    favorite_genres = UserFavouriteGenre.objects.filter(user=request.user)
    active_tab = request.GET.get("tab", "reviewed")

    # Sorting logic
    sort_option = request.GET.get("sort", "rating-desc")
    if sort_option == "rating-asc":
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

    if active_tab == "to-review":
        user_genres = [fav.genre for fav in favorite_genres]
        to_review_media = (
            Media.objects.filter(genres__in=user_genres)
            .distinct()
            .exclude(review__user=request.user)
        )
        context["to_review_media"] = to_review_media

    elif active_tab == "liked":
        liked_reviews = Review.objects.filter(reviewlike__user=request.user).order_by(order_by_field)
        liked_review_ids = ReviewLike.objects.filter(user=request.user).values_list('review_id', flat=True)
        context["liked_reviews"] = liked_reviews
        context["liked_review_ids"] = list(liked_review_ids)

    else:
        reviewed_reviews = Review.objects.filter(user=request.user).order_by(order_by_field)
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

            # If user checked the "Remove Profile Picture" box
            if "delete_picture" in request.POST:
                if user_profile.profile_picture:
                    user_profile.profile_picture.delete(save=False)
                user_profile.profile_picture = None
                user_profile.save()

            # Handle genres
            selected_genres = request.POST.getlist("favorite_genres")
            removed_genres_str = request.POST.get("removed_genres", "")
            if removed_genres_str:
                removed_ids = removed_genres_str.split(",")
                UserFavouriteGenre.objects.filter(
                    user=request.user,
                    genre__genre_id__in=removed_ids
                ).delete()

            for genre_id in selected_genres:
                genre_obj, _ = Genre.objects.get_or_create(genre_id=genre_id)
                UserFavouriteGenre.objects.get_or_create(user=request.user, genre=genre_obj)

            # Redirect to the profile page after saving
            return redirect("ScreenCritic:profile")

    else:
        form = ProfileEditForm(instance=user_profile)

    return render(request, "ScreenCritic/edit_profile.html", {
        "form": form,
        "user_profile": user_profile,
        "genres": genres,
        "user_favorite_genres": user_favorite_genres,
    })