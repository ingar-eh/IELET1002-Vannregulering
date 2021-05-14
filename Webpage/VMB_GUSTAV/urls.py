from django.urls import path
from .views import home, aboutUs, graphical, memes, login_view, register_view, logout_view



"""
When conecting to a specific url from the site that maches the paths in the list
Go to the home method of views.py and take the user connection request object with it 
"""
urlpatterns = [
    path("", home, name="Homepage of the app"),
    path("aboutUs/", aboutUs, name="The page for more info on the project"),
    path("graphical/", graphical, name="graphical"),
    path("memes/", memes, name="memes LOL"),
    path("login/", login_view, name="Login"),
    path("register/", register_view, name="Register"),
    path("logout/", logout_view, name="Logout")
]


