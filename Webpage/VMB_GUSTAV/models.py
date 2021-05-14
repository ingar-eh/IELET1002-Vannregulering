from django.db import models
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms

# Create your models here.
"""
Create object that holds data for about uss page
Once the page loads, display data
"""
class aboutUsInfo(models.Model):
    header = ""
    name = ""
    text = ""
    picture = ""


"""
Create object that saves file location of a picture
"""
class meme():
    picture = ""


"""
Create object that holds data for register page
Object innherits from UserCreationForm, a prebuilt instance of django that takes care of the hard stuff for uss
Once the page loads, display data and style it
The methods in instance have custom style
"""
class registerForm(UserCreationForm):
    """
    Username:
        - Label
        - minimum input
        - maximum input
        - strip all white spaces in the usrename
        - Text input:
            + AUtocomplete if have the same in database
            + The placeholder for what is inside input field when nothing is inside
    """
    username = forms.CharField(
        label="Username",
        min_length=8,
        max_length=32,
        strip=False,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "new-username",
                "placeholder": "Username",
                }
            ),
        )

    """
    Password
        - set form to password input
    """
    password1 = forms.CharField(
        label="Password",
        min_length=8,
        max_length=64,
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": 'new-password',
                "placeholder": "Password",
                }
            ),
        )
    
    password2 = forms.CharField(
        label="Password confirm",
        min_length=8,
        max_length=64,
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": 'new-password',
                "placeholder": "Password confirm",
                }
            ),
        )

    
class loginForm(AuthenticationForm):
    # Username
    username = forms.CharField(
        label="Username",
        min_length=8,
        max_length=32,
        strip=False,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "new-username",
                "placeholder": "Username",
                }
            ),
        )

    # Password
    password = forms.CharField(
        label="Password",
        min_length=8,
        max_length=64,
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": 'new-password',
                "placeholder": "Password",
                }
            ),
        )