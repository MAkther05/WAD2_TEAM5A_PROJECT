from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse 
from django.db.models import Count, Avg
from ScreenCritic.models import Media, Review

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

    context = {
        'media': media,
        'reviews': reviews,
        'recommended_media': recommended_media,
        'total_ratings': total_ratings,
        'average_rating': average_rating,
        'text_reviews_count': text_reviews_count,
        'current_sort': sort_by
    }

    return render(request, 'ScreenCritic/title.html', context)