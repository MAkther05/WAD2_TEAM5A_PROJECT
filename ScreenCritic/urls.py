from django.urls import path
from ScreenCritic import views

app_name = 'ScreenCritic'

urlpatterns = [
    path('', views.home, name='home'),  
    path('home/', views.home, name='home'),
    path('login_register/', views.login_register, name = 'login_register'),
    path('logout/', views.user_logout, name = "user_logout"),
    path('delete_account/', views.deleteuser, name = 'delete_account'),

    
    # TV Shows
    path('tv/', views.tv_list, name='tv_list'),
    path('tv/<slug:slug>/', views.media_detail, {'media_type': 'TV Show'}, name='tv_detail'),
    path('tv/<slug:slug>/review/', views.media_review, {'media_type': 'TV Show'}, name='tv_review'),

    # Movies
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/<slug:slug>/', views.media_detail, {'media_type': 'Movie'}, name='movie_detail'),
    path('movies/<slug:slug>/review/', views.media_review, {'media_type': 'Movie'}, name='movie_review'),

    # Games
    path('games/', views.game_list, name='game_list'),
    path('games/<slug:slug>/', views.media_detail, {'media_type': 'Game'}, name='game_detail'),
    path('games/<slug:slug>/review/', views.media_review, {'media_type': 'Game'}, name='game_review'),

    path('review/<int:review_id>/like/', views.like_review, name='like_review'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile_by_username'),

    path('search/', views.live_search, name='live_search'),

    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/<int:subscription_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('toggle-subscription/<int:media_id>/', views.toggle_subscription, name='toggle_subscription'),
]