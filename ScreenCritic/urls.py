from django.urls import path 
from ScreenCritic import views

app_name = 'ScreenCritic'
urlpatterns = [
    path('home/', views.home, name='home'),

    path('login-register/', views.login_register, name='login_register'),
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
]