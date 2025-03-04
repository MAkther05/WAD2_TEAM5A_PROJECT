from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Genre(models.Model):
    genre_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Media(models.Model):
    media_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    type = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='cover_images/', blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    release_date = models.DateTimeField()
    genres = models.ManyToManyField(Genre, related_name="media")

    def save(self, *args, **kwargs):
        if not self.slug: #only generate slug if not already defined
            original_slug = slugify(self.title)
            slug = original_slug
            counter = 1
            while Media.objects.filter(slug=slug).exists(): #if the same slug already exists then add counter
                slug = f"{original_slug}_{counter}"
                counter += 1
            self.slug = slug
        super(Media, self).save(*args, **kwargs)

    @property
    def average_rating(self):
        return Review.objects.filter(media_id=self).aggregate(models.Avg('rating'))['rating__avg'] or 0

    def __str__(self):
        return self.title

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    review = models.TextField(blank=True, null=True)
    rating = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    @property
    def total_likes(self):
        return ReviewLike.objects.filter(review=self).count()

    def __str__(self):
        return self.user.username + "'s review of " + self.media.title
    
class ReviewLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    date_liked = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'review'),)

    def __str__(self):
        return f"{self.user.username} liked {self.review}"
    
class UserMediaSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'media'),)

    def __str__(self):
        return self.user.username + " subscribed to " + self.media.title
    
class UserFavouriteGenre(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'genre'),)

    def __str__(self):
        return f"{self.user.username} loves {self.genre.name}"