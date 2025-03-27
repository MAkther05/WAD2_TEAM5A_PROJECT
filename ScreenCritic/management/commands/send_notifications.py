from django.core.management.base import BaseCommand
from django.utils import timezone
from ScreenCritic.models import UserMediaSubscription, Media

class Command(BaseCommand):
    help = 'Check for media releases and create notifications'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        
        # Find media items released today
        releases_today = Media.objects.filter(
            release_date__date=today,
            usermediasubscription__is_released=False  # Only get unreleased subscriptions
        ).distinct()

        for release in releases_today:
            # Get all subscriptions for this media that haven't been marked as released
            subscriptions = UserMediaSubscription.objects.filter(
                media=release,
                is_released=False
            )
            
            for subscription in subscriptions:
                # Mark as released and set notification date
                subscription.is_released = True
                subscription.notification_date = timezone.now()
                subscription.save()
                
                self.stdout.write(f'Created notification for {subscription.user.username} about {release.title}')

        self.stdout.write('Release notifications created.') 