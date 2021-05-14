from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
import os

# Get dataframe objects from moduels 
from .models import aboutUsInfo, meme, registerForm, loginForm


# Global variables -----
"""
Get current active directory because we need a static directory to save data from the server
"""
cwd = os.getcwd() + "/VMB_GUSTAV/"  # Get the current working directory (cwd)

# Create your views here.
def home(request):
    """
    Render the "homepage.html" to the object that requested the conection
    """
    return render(request, "homepage.html")


def aboutUs(request):
    # Variables -----
    headerList = [
        "Modellering og kommunikasjon",
        "Elektronikk",
        "Arduino",
        "Kommunikasjon",
        "Data",
        "Nettside"
    ]
    nameList = [
        "Admir",
        "Odd Arne",
        "Ingar",
        "Hans",
        "Simeon",
        "Martynas"
    ]
    fileNameList = [
        "Admir.txt",
        "Odd_Arne.txt",
        "Ingar.txt",
        "Hans.txt",
        "Simeon.txt",
        "Martynas.txt"
    ]
    picNameList = [
        "Admir.jpg",
        "Odd_Arne.jpg",
        "Ingar.jpg",
        "Hans.jpg",
        "Simeon.jpg",
        "Martynas.jpg"
    ]

    # Create data dictionary that we will pass on to the page on render
    data = {
        "intro": "",
        "infoList": []
    }

    # Get intro data
    with open(cwd + "data/AboutUsData/intro.txt", "r") as file:
        for d in file.readlines():
            data["intro"] += d + "  "
    
    # Give info to data dictionary
    for i in range(len(fileNameList)):
        # Make new module object
        personObject = aboutUsInfo()

        # Give object data
        personObject.header = headerList[i]
        personObject.name = nameList[i]
        personObject.picture = "pictures/AboutUs/" + picNameList[i]
        personObject.text = ""

        with open(cwd + "data/AboutUsData/" + fileNameList[i], "r") as file:
            for d in file.readlines():
                personObject.text += d + "  "
        
        # Give all the info to the data dictionary
        data["infoList"] += [personObject]

    # Render content with data
    return render(request, "aboutUs.html", data)


def memes(request):
    # Set picture directory
    pictureDir = cwd + "static/pictures/Memes/"

    """
    Get all the file names in directory
    Directory only has pictures so we have raw picture file names from the directory
    """
    pictureFiles = []

    for pictureName in os.listdir(pictureDir):
        # Make a new object that has "memes" model
        memeObject = meme()

        # Add properties to the object
        memeObject.picture = "pictures/Memes/" + pictureName

        # Save object to the list
        pictureFiles += [memeObject]

    # Put data in
    data = {
        "pictureList": pictureFiles
    }

    # Render the website with the given data
    return render(request, "memes.html", data)


def register_view(request):
    """
    We check if the server is getting data or is being asked to send data
    We do this by checking the client signal that is being sent by the client in "request"
    request has form "method" that can be set to either POST or GET method depending on the form
    We send data when the page is first rendered "GET"
    We get data wehn the user has submited a form "POST"
    """
    if request.method == "POST":
        """
        We create a new instance of a form that has the data that was sent to server by the client using "POST" method
        The instance takes that data and validates if its is maching or not, this function is prbuilt in django
        """
        form = registerForm(data=request.POST)

        """
        Check if the form data sent by the user is valid
        is_valid() is a inbuilt method in the User form instance created by django
        If form is valid save it to the database
        """
        if form.is_valid():
            """
            Save the new user into data base and get user that is trying to log in
            save() is a inbuilt method in user form insatnce for django
            We execute the method for the user to save the user information
            the save() method returns user information so we save it
            """
            user = form.save()
            
            """
            Log in the user
            The login() method in django takes inn the client and the user login information
            Login() then takes and passes that information to the client so that it is loged in with the corect login information
            """
            login(request, user)

            # If everything sucesfull redirect to the homepage
            return redirect("/")
    elif request.method == "GET":
        # Create a new instance of the creation form, a inbuilt django instance
        form = registerForm()

    """
    Once we render the page send form instance aswell
    If its GET send a brand new form
    If its POST that has invalid data send that data back
    """
    return render(request, "register.html", {"form": form})


def login_view(request):
    # Check if POST or GET request
    if request.method == "POST":
        """
        Create a new authentication form insatnce
        Pass the information the client has sent into authentication instance from the POST method
        Since this is a prebuilt django instance everything is inside
        """
        auth = loginForm(data=request.POST)

        # Check if the user exist
        if auth.is_valid():
            # Get user that is trying to log in
            user = auth.get_user()

            """
            Get user that is trying to log in
            get_user() is a inbuilt mathod in django authentication instance
            """
            login(request, user)

            # If everything sucesfull redirect to the homepage
            return redirect("/")
    elif request.method == "GET":
        # Create a new authentication form insatnce
        auth = loginForm()
    
    """
    Once we render the page send authentication instance aswell
    If its GET send a brand new authentication
    If its POST that has invalid data send that data back
    """
    return render(request, "login.html", {"auth": auth})


def logout_view(request):
    # Check if request has been sent from the user
    if request.method == "POST":
        """
        Logout the user that is already loged in
        logout is a pre built method in django
        We pass down the request client data to the logout to log client out
        """
        logout(request)

        # Return the client to the homepage
        return redirect("/")


def graphical(request):
    return render(request, "graphical.html")