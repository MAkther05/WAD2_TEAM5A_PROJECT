from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from ScreenCritic.models import Media, Review, ReviewLike, Genre, UserProfile, UserMediaSubscription, UserFavouriteGenre
from ScreenCritic.forms import ProfileEditForm, LoginForm, RegisterForm, ReviewForm

class MediaModelTest(TestCase):
    def setUp(self): #setup test data before each test method
        #create test genres
        self.genre1 = Genre.objects.create(name="Action")
        self.genre2 = Genre.objects.create(name="Drama")
        
        #create test media
        self.media = Media.objects.create(
            title="Test Movie",
            type="Movie",
            description="Test Description",
            release_date=timezone.now(),
            creator="Test Director"
        )
        self.media.genres.add(self.genre1, self.genre2)

    def test_media_creation(self): #check if media is created with correct attributes
        self.assertEqual(self.media.title, "Test Movie") #check if title is correct
        self.assertEqual(self.media.type, "Movie") #check if type is correct
        self.assertEqual(self.media.description, "Test Description") #check if description is correct
        self.assertEqual(self.media.creator, "Test Director") #check if creator is correct
        self.assertEqual(list(self.media.genres.all()), [self.genre1, self.genre2]) #check if genres are correctly associated

    def test_media_str(self): #check if media is represented as a string correctly
        self.assertEqual(str(self.media), "Test Movie")

    def test_media_slug_generation(self): #check if slug is generated correctly
        self.assertTrue(self.media.slug) #check if slug exists
        self.assertEqual(self.media.slug, "test-movie") #check if slug is correctly formatted

    def test_media_average_rating(self): #check if average rating is calculated correctly
        #create test user
        user = User.objects.create_user(username="testuser", password="testpass")
        
        #create test reviews
        Review.objects.create(user=user, media=self.media, rating=5, review="Great!")
        Review.objects.create(user=user, media=self.media, rating=3, review="Okay")
        
        self.assertEqual(self.media.average_rating, 4.0) #check if average is calculated correctly

class ReviewModelTest(TestCase):
    def setUp(self): #setup test data before each test method
        #create test user
        self.user = User.objects.create_user(username="testuser", password="testpass")
        
        #create test media
        self.media = Media.objects.create(
            title="Test Movie",
            type="Movie",
            release_date=timezone.now()
        )
        
        #create test review
        self.review = Review.objects.create(
            user=self.user,
            media=self.media,
            rating=5,
            review="Great movie!"
        )

    def test_review_creation(self): #check if review is created with correct attributes
        self.assertEqual(self.review.user, self.user) #check if user is correct
        self.assertEqual(self.review.media, self.media) #check if media is correct
        self.assertEqual(self.review.rating, 5) #check if rating is correct
        self.assertEqual(self.review.review, "Great movie!") #check if review text is correct

    def test_review_str(self): #check if review is represented as a string correctly
        expected_str = f"{self.user.username}'s review of {self.media.title}"
        self.assertEqual(str(self.review), expected_str)

    def test_review_total_likes(self): #check if total likes are counted correctly
        #create test likes
        user2 = User.objects.create_user(username="testuser2", password="testpass")
        ReviewLike.objects.create(user=user2, review=self.review)
        
        self.assertEqual(self.review.total_likes, 1) #check if like count is correct

class ViewsTest(TestCase):
    def setUp(self): #setup test data before each test method
        #create test client
        self.client = Client()
        
        #create test user
        self.user = User.objects.create_user(username="testuser", password="testpass")
        UserProfile.objects.create(user=self.user, email="test@example.com")
        
        #create test genres
        self.genre = Genre.objects.create(name="Action")
        
        #create test media
        self.media = Media.objects.create(
            title="Test Movie",
            type="Movie",
            description="Test Description",
            release_date=timezone.now(),
            creator="Test Director"
        )
        self.media.genres.add(self.genre)
        
        #create test review
        self.review = Review.objects.create(
            user=self.user,
            media=self.media,
            rating=5,
            review="Great movie!"
        )

    def test_home_view(self): #check if home view works correctly
        response = self.client.get(reverse('ScreenCritic:home'))
        self.assertEqual(response.status_code, 200) #check if response status is correct
        self.assertTemplateUsed(response, 'ScreenCritic/base.html') #check if correct template is used

    def test_movie_list_view(self): #check if movie list view works correctly
        response = self.client.get(reverse('ScreenCritic:movie_list'))
        self.assertEqual(response.status_code, 200) #check if response status is correct
        self.assertTemplateUsed(response, 'ScreenCritic/media.html') #check if correct template is used
        self.assertIn('media_list', response.context) #check if media list is in context
        self.assertIn('media_type', response.context) #check if media type is in context
        self.assertEqual(response.context['media_type'], 'Movies') #check if media type is correct

    def test_tv_list_view(self): #check if TV list view works correctly
        response = self.client.get(reverse('ScreenCritic:tv_list'))
        self.assertEqual(response.status_code, 200) #check if response status is correct
        self.assertTemplateUsed(response, 'ScreenCritic/media.html') #check if correct template is used
        self.assertIn('media_list', response.context) #check if media list is in context
        self.assertIn('media_type', response.context) #check if media type is in context
        self.assertEqual(response.context['media_type'], 'TV Shows') #check if media type is correct

    def test_game_list_view(self): #check if game list view works correctly
        response = self.client.get(reverse('ScreenCritic:game_list'))
        self.assertEqual(response.status_code, 200) #check if response status is correct
        self.assertTemplateUsed(response, 'ScreenCritic/media.html') #check if correct template is used
        self.assertIn('media_list', response.context) #check if media list is in context
        self.assertIn('media_type', response.context) #check if media type is in context
        self.assertEqual(response.context['media_type'], 'Games') #check if media type is correct

    def test_media_detail_view(self): #check if media detail view works correctly
        response = self.client.get(reverse('ScreenCritic:media_detail', kwargs={'slug': self.media.slug, 'media_type': 'Movie'}))
        self.assertEqual(response.status_code, 200) #check if response status is correct
        self.assertTemplateUsed(response, 'ScreenCritic/title.html') #check if correct template is used
        self.assertIn('media', response.context) #check if media is in context
        self.assertIn('reviews', response.context) #check if reviews are in context
        self.assertIn('total_ratings', response.context) #check if total ratings is in context
        self.assertIn('average_rating', response.context) #check if average rating is in context
        self.assertIn('text_reviews_count', response.context) #check if text reviews count is in context
        self.assertIn('recommended_media', response.context) #check if recommended media is in context
        self.assertIn('current_sort', response.context) #check if current sort is in context
        self.assertIn('liked_reviews', response.context) #check if liked reviews is in context

    def test_like_review_view_authenticated(self): #check if like review view works for authenticated users
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(reverse('ScreenCritic:like_review', kwargs={'review_id': self.review.review_id}))
        self.assertEqual(response.status_code, 200) #check if response status is correct
        self.assertIn('likes', response.json()) #check if likes count is in response
        self.assertIn('liked', response.json()) #check if liked status is in response

    def test_like_review_view_unauthenticated(self): #check if like review view handles unauthenticated users correctly
        response = self.client.post(reverse('ScreenCritic:like_review', kwargs={'review_id': self.review.review_id}))
        self.assertEqual(response.status_code, 401) #check if unauthorized response is returned

    def test_suggested_content(self): #check if suggested content functionality works correctly
        #create user favorite genre
        UserFavouriteGenre.objects.create(user=self.user, genre=self.genre)
        
        #login user
        self.client.login(username="testuser", password="testpass")
        
        #test movie list view with suggested content
        response = self.client.get(reverse('ScreenCritic:movie_list'))
        self.assertIn('suggested_movies', response.context) #check if suggested movies is in context
        self.assertIn(self.media, response.context['suggested_movies']) #check if media is in suggested movies

    def test_media_review_view_authenticated(self): #check if media review view works for authenticated users
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('ScreenCritic:media_review', kwargs={'slug': self.media.slug, 'media_type': 'Movie'}))
        self.assertEqual(response.status_code, 200) #check if response status is correct
        self.assertTemplateUsed(response, 'ScreenCritic/write_review.html') #check if correct template is used
        self.assertIn('form', response.context) #check if form is in context
        self.assertIn('media', response.context) #check if media is in context

    def test_media_review_view_unauthenticated(self): #check if media review view handles unauthenticated users correctly
        response = self.client.get(reverse('ScreenCritic:media_review', kwargs={'slug': self.media.slug, 'media_type': 'Movie'}))
        self.assertRedirects(response, '/login/?next=/review/Test-Movie/Movie/') #check if redirects to login

    def test_login_register_view_get(self): #check if login/register view works for GET requests
        response = self.client.get(reverse('ScreenCritic:login_register'))
        self.assertEqual(response.status_code, 200) #check if response status is correct
        self.assertTemplateUsed(response, 'ScreenCritic/login_register.html') #check if correct template is used
        self.assertIn('login_form', response.context) #check if login form is in context
        self.assertIn('register_form', response.context) #check if register form is in context

    def test_login_register_view_post_login(self): #check if login/register view handles login POST requests correctly
        response = self.client.post(reverse('ScreenCritic:login_register'), {
            'form_type': 'login',
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertRedirects(response, reverse('ScreenCritic:home')) #check if redirects to home after login

    def test_login_register_view_post_register(self): #check if login/register view handles registration POST requests correctly
        response = self.client.post(reverse('ScreenCritic:login_register'), {
            'form_type': 'register',
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertRedirects(response, reverse('ScreenCritic:home')) #check if redirects to home after registration
        self.assertTrue(User.objects.filter(username='newuser').exists()) #check if user was created

    def test_user_logout_view(self): #check if logout view works correctly
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('ScreenCritic:user_logout'))
        self.assertRedirects(response, reverse('ScreenCritic:home')) #check if redirects to home after logout

    def test_profile_view_authenticated(self): #check if profile view works for authenticated users
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('ScreenCritic:profile'))
        self.assertEqual(response.status_code, 200) #check if response status is correct
        self.assertTemplateUsed(response, 'ScreenCritic/profile.html') #check if correct template is used
        self.assertIn('user_profile', response.context) #check if user profile is in context
        self.assertIn('favorite_genres', response.context) #check if favorite genres is in context
        self.assertIn('active_tab', response.context) #check if active tab is in context
        self.assertIn('current_sort', response.context) #check if current sort is in context

    def test_profile_view_unauthenticated(self): #check if profile view handles unauthenticated users correctly
        response = self.client.get(reverse('ScreenCritic:profile'))
        self.assertRedirects(response, '/login/?next=/profile/') #check if redirects to login

    def test_edit_profile_view_authenticated(self): #check if edit profile view works for authenticated users
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('ScreenCritic:edit_profile'))
        self.assertEqual(response.status_code, 200) #check if response status is correct
        self.assertTemplateUsed(response, 'ScreenCritic/edit_profile.html') #check if correct template is used
        self.assertIn('form', response.context) #check if form is in context
        self.assertIn('user_profile', response.context) #check if user profile is in context
        self.assertIn('genres', response.context) #check if genres is in context
        self.assertIn('user_favorite_genres', response.context) #check if user favorite genres is in context

    def test_edit_profile_view_unauthenticated(self): #check if edit profile view handles unauthenticated users correctly
        response = self.client.get(reverse('ScreenCritic:edit_profile'))
        self.assertRedirects(response, '/login/?next=/edit_profile/') #check if redirects to login

    def test_edit_profile_form_submission(self): #check if edit profile form submission works correctly
        self.client.login(username="testuser", password="testpass")
        data = {
            'email': 'newemail@example.com',
            'bio': 'New bio',
            'favorite_genres': [self.genre.genre_id]
        }
        response = self.client.post(reverse('ScreenCritic:edit_profile'), data)
        self.assertRedirects(response, reverse('ScreenCritic:profile')) #check if redirects to profile after submission
        
        #verify changes were saved
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.email, 'newemail@example.com') #check if email was updated
        self.assertEqual(updated_profile.bio, 'New bio') #check if bio was updated
        self.assertTrue(UserFavouriteGenre.objects.filter(user=self.user, genre=self.genre).exists()) #check if favorite genre was added

class UserProfileModelTest(TestCase):
    def setUp(self): #setup test data before each test method
        #create test user
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.profile = UserProfile.objects.create(
            user=self.user,
            email="test@example.com",
            password="testpass"
        )

    def test_profile_creation(self): #check if profile is created with correct attributes
        self.assertEqual(self.profile.user, self.user) #check if user is correct
        self.assertEqual(self.profile.email, "test@example.com") #check if email is correct
        self.assertEqual(self.profile.password, "testpass") #check if password is correct

    def test_profile_str(self): #check if profile is represented as a string correctly
        self.assertEqual(str(self.profile), "testuser")

class UserMediaSubscriptionTest(TestCase):
    def setUp(self): #setup test data before each test method
        #create test user
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.media = Media.objects.create(
            title="Test Movie",
            type="Movie",
            release_date=timezone.now()
        )
        self.subscription = UserMediaSubscription.objects.create(
            user=self.user,
            media=self.media
        )

    def test_subscription_creation(self): #check if subscription is created with correct attributes
        self.assertEqual(self.subscription.user, self.user) #check if user is correct
        self.assertEqual(self.subscription.media, self.media) #check if media is correct

    def test_subscription_str(self): #check if subscription is represented as a string correctly
        expected_str = f"{self.user.username} subscribed to {self.media.title}"
        self.assertEqual(str(self.subscription), expected_str)

class UserFavouriteGenreTest(TestCase):
    def setUp(self): #setup test data before each test method
        #create test user
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.genre = Genre.objects.create(name="Action")
        self.favourite = UserFavouriteGenre.objects.create(
            user=self.user,
            genre=self.genre
        )

    def test_favourite_creation(self): #check if favorite genre is created with correct attributes
        self.assertEqual(self.favourite.user, self.user) #check if user is correct
        self.assertEqual(self.favourite.genre, self.genre) #check if genre is correct

    def test_favourite_str(self): #check if favorite genre is represented as a string correctly
        expected_str = f"{self.user.username} loves {self.genre.name}"
        self.assertEqual(str(self.favourite), expected_str)

class GenreModelTest(TestCase):
    def setUp(self): #setup test data before each test method
        #create test genre
        self.genre = Genre.objects.create(name="Action")

    def test_genre_creation(self): #check if genre is created with correct attributes
        self.assertEqual(self.genre.name, "Action") #check if name is correct

    def test_genre_str(self): #check if genre is represented as a string correctly
        self.assertEqual(str(self.genre), "Action")
