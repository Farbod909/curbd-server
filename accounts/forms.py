from django import forms

from .admin import UserCreationForm


class UserLoginForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(UserCreationForm):
    is_host = forms.BooleanField(label='Would you like to be a host?', required=False)
