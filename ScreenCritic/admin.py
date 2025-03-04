from django.contrib import admin
from .models import UserProfile, Media, Review, UserMediaSubscription, Genre, ReviewLike, UserFavouriteGenre

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ('user__username',) #search users by username

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    search_fields = ('title', 'description',)  #search media by title
    list_filter = ('type',)  #filter sidebar by type

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ('name',)  #search genres by genre name

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    search_fields = ('username__username', 'media_id__title',)  #search reviews by username or media title

@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    search_fields = ('user__username',)  #search review likes by username

@admin.register(UserMediaSubscription)
class UserMediaSubscriptionAdmin(admin.ModelAdmin):
    search_fields = ('username__username', 'media_id__title',)  #search subscriptions by username or media title

@admin.register(UserFavouriteGenre)
class UserFavouriteGenreAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'genre__name',)  #search favourite genres by username and genre name
