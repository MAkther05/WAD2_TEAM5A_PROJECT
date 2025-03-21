from datetime import datetime
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse 
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.http import HttpResponse
from .forms import ReviewForm, UserForm, UserProfileForm
from django.contrib.auth.models import User

from WAD2_TEAM5A_PROJECT import settings

def home(request):
    visitor_cookie_handler(request)
    return render(request, 'ScreenCritic/base.html')

def login_register(request):
    registered = False

    if request.method == "POST":
        if "login" in request.POST:  # Login form submitted
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    login(request, user)
                    return redirect(reverse("ScreenCritic:index"))
                else:
                    return HttpResponse("Your ScreenCritic account is disabled.")
            else:
                return HttpResponse("Invalid login details supplied.")

        elif "register" in request.POST:  # Registration form submitted
            user_form = UserForm(request.POST)
            profile_form = UserProfileForm(request.POST, request.FILES)

            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save()
                user.set_password(user.password)  # Hash the password
                user.save()

                profile = profile_form.save(commit=False)
                profile.user = user

                if "profile_picture" in request.FILES:
                    profile.profile_picture = request.FILES["profile_picture"]

                profile.save()
                registered = True
            else:
                print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,"ScreenCritic/login_register.html",{"user_form": user_form, "profile_form": profile_form, "registered": registered},)



def write_review(request):
    
    
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user  # Assuming the user is logged in
            #review.media = media
            review.save()
            return redirect('ScreenCritic:index')  # Redirect to media detail page
    else:
        form = ReviewForm()
    
    return render(request, 'ScreenCritic/review.html', {'form': form})

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

# Updated the function definition
def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')
    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie
    # Update/set the visits cookie
    request.session['visits'] = visits