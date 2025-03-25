from django.urls import path
from ScreenCritic import views

app_name = 'ScreenCritic'

urlpatterns = [
    path('', views.home, name='home'),  

   
    path('tv/', views.tv_list, name='tv_list'),
    path('tv/<slug:slug>/', views.media_detail, {'media_type': 'TV Show'}, name='tv_detail'),

    
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/<slug:slug>/', views.media_detail, {'media_type': 'Movie'}, name='movie_detail'),

    
    path('games/', views.game_list, name='game_list'),
    path('games/<slug:slug>/', views.media_detail, {'media_type': 'Game'}, name='game_detail'),

    
    path('review/<int:review_id>/like/', views.like_review, name='like_review'),
]
