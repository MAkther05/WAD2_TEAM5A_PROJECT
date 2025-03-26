from django import forms
from .models import Review, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import UserProfile, UserFavouriteGenre, Genre

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review']
        widgets = {
            'review': forms.Textarea(attrs={
                'placeholder': 'Write your detailed review here...',
                'rows': 5
            })
        }

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

# forms.py
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make password requirements less strict
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            UserProfile.objects.create(user=user, email=user.email)
        return user

class ProfileEditForm(forms.ModelForm):
    favorite_genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),  # Fetch genres instead of UserFavouriteGenre
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio', 'favorite_genres']
