from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Testimony, Rating
from django.contrib.auth.models import User
from .models import ProductRating


class RatingForm(forms.ModelForm):
    class Meta:
        model = ProductRating
        fields = ['rating']  # We only need the rating field for submission


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'image']


class TestimonyForm(forms.ModelForm):
    class Meta:
        model = Testimony
        fields = ['content']


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'product']


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='Your Name')
    email = forms.EmailField(label='Your Email')
    message = forms.CharField(widget=forms.Textarea, label='Your Message')


class ModelForm:
    pass
