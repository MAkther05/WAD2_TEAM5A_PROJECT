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

class Media(models.Model):
    media_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    type = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='cover_images/', blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    release_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Media, self).save(*args, **kwargs)

    @property
    def average_rating(self):
        return Review.objects.filter(media_id=self).aggregate(models.Avg('rating'))['rating__avg'] or 0

    def __str__(self):
        return self.title

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    media_id = models.ForeignKey(Media, on_delete=models.CASCADE)
    review = models.TextField(blank=True, null=True)
    rating = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.username.username + "-" + self.media_id.title

class UserMediaSubscription(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    media_id = models.ForeignKey(Media, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('username', 'media_id'),)

    def __str__(self):
        return self.username.username + " subscribed to " + self.media_id.title