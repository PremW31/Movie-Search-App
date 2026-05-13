# testapp/views.py

import requests

from requests.exceptions import RequestException

from django.shortcuts import render, redirect

from django.contrib.auth.models import User

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required


API_KEY = "c93475570e38be796fc63837deeb68b1"


# HOME PAGE
@login_required(login_url='login')
def home(request):

    movies = []

    trending_movies = []

    error = None

    # TRENDING MOVIES
    trending_url = (
        f"https://api.themoviedb.org/3/trending/movie/week"
        f"?api_key={API_KEY}"
    )

    try:

        trending_response = requests.get(
            trending_url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        trending_data = trending_response.json()

        trending_results = trending_data.get("results", [])

        for movie in trending_results[:8]:

            trending_movies.append({

                "title": movie.get("title"),

                "poster": movie.get("poster_path"),

                "rating": movie.get("vote_average"),

            })

    except RequestException as e:

        error = str(e)

    # SEARCH MOVIES
    if request.method == "POST":

        movie_name = request.POST.get("movie")

        search_url = "https://api.themoviedb.org/3/search/movie"

        params = {
            "api_key": API_KEY,
            "query": movie_name
        }

        try:

            response = requests.get(
                search_url,
                params=params,
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            data = response.json()

            results = data.get("results", [])

            # ONLY 5 MOVIES
            for movie in results[:5]:

                movie_id = movie.get("id")

                # TRAILER API
                video_url = (
                    f"https://api.themoviedb.org/3/movie/"
                    f"{movie_id}/videos"
                )

                try:

                    video_response = requests.get(
                        video_url,
                        params={"api_key": API_KEY},
                        timeout=10,
                        headers={
                            "User-Agent": "Mozilla/5.0"
                        }
                    )

                    video_data = video_response.json()

                except RequestException:

                    video_data = {"results": []}

                trailer_link = ""

                for video in video_data.get("results", []):

                    if (
                        video.get("type") == "Trailer"
                        and video.get("site") == "YouTube"
                    ):

                        trailer_key = video.get("key")

                        trailer_link = (
                            f"https://www.youtube.com/watch?v="
                            f"{trailer_key}"
                        )

                        break

                # OTT PROVIDER API
                provider_url = (
                    f"https://api.themoviedb.org/3/movie/"
                    f"{movie_id}/watch/providers"
                )

                try:

                    provider_response = requests.get(
                        provider_url,
                        params={"api_key": API_KEY},
                        timeout=10,
                        headers={
                            "User-Agent": "Mozilla/5.0"
                        }
                    )

                    provider_data = provider_response.json()

                except RequestException:

                    provider_data = {"results": {}}

                ott_platforms = []

                ott_link = ""

                india_data = (
                    provider_data.get("results", {}).get("IN")
                )

                if india_data:

                    ott_link = india_data.get("link", "")

                    flatrate = india_data.get(
                        "flatrate",
                        []
                    )

                    for ott in flatrate:

                        ott_platforms.append(
                            ott.get("provider_name")
                        )

                movies.append({
                    "id": movie.get("id"), 

                    "title": movie.get("title"),

                    "overview": movie.get("overview"),

                    "rating": movie.get("vote_average"),

                    "poster": movie.get("poster_path"),

                    "ott": ott_platforms,

                    "ott_link": ott_link,

                    "trailer": trailer_link

                })

        except RequestException as e:

            error = str(e)

    return render(request, "home.html", {

        "movies": movies,

        "trending_movies": trending_movies,

        "error": error

    })


# SIGNUP
def signup_view(request):

    error = ""

    if request.method == "POST":

        username = request.POST.get("username")

        email = request.POST.get("email")

        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():

            error = "Username already exists"

        else:

            User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # AUTO LOGIN AFTER SIGNUP
            user = authenticate(
                username=username,
                password=password
            )

            login(request, user)

            return redirect("home")

    return render(request, "signup.html", {

        "error": error

    })


# LOGIN
def login_view(request):

    error = ""

    if request.method == "POST":

        username = request.POST.get("username")

        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("home")

        else:

            error = "Invalid username or password"

    return render(request, "login.html", {

        "error": error

    })


# LOGOUT
def logout_view(request):

    logout(request)

    return redirect("login")

from .models import Favorite

def add_favorite(request):

    if request.method == "POST":

        movie_id = request.POST.get("movie_id")
        title = request.POST.get("title")
        poster = request.POST.get("poster")

        Favorite.objects.get_or_create(
            user=request.user,
            movie_id=movie_id,
            title=title,
            poster=poster
        )

    return redirect("home")

def add_favorite(request):

    if request.method == "POST":

        movie_id = request.POST.get("movie_id")

        if not movie_id:   # 🔥 prevent crash
            return redirect("home")

        Favorite.objects.get_or_create(
            user=request.user,
            movie_id=int(movie_id),
            title=request.POST.get("title"),
            poster=request.POST.get("poster")
        )

    return redirect("home")