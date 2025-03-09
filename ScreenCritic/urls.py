from django.urls import path 
from ScreenCritic import views

app_name = 'ScreenCritic'
urlpatterns = [
    path('', views.home, name='home'),
    
]