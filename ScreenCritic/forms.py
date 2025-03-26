from django import forms
from .models import UserProfile, UserFavouriteGenre, Genre

class ProfileEditForm(forms.ModelForm):
    favorite_genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),  # Fetch genres instead of UserFavouriteGenre
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio', 'favorite_genres']
