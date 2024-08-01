from django.contrib.auth import logout
from django.shortcuts import redirect


def sign_in(request):
    return redirect("/oauth2/start")


def sign_out(request):
    logout(request)
    return redirect("/oauth2/sign_out")
