"""WAD2_TEAM5A_PROJECT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
from ScreenCritic import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("ScreenCritic/", include("django.contrib.auth.urls")),
    path('', views.home, name='home'),
    path('password_change/',auth_views.PasswordChangeView.as_view(template_name='ScreenCritic/change_password.html',success_url='/ScreenCritic/profile'),name='password_change'),
    path('admin/', admin.site.urls),
    path('ScreenCritic/', include('ScreenCritic.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
