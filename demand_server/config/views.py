from django.shortcuts import render

def landing(request):
    return render(request, "landing.html") 


def main(request):
    return render(request, "main.html")

def login(request):
    return render(request, "accounts/login_modal.html")