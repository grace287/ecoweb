from django.shortcuts import render
from django.http import HttpResponse

def main(request):
    return render(request, 'main.html') 

# def main(request):
#     return HttpResponse("Hello, world!")

def provider_login(request):
    return render(request, 'accounts/provider_login.html')

def login(request):
    return render(request, 'accounts/provider_login.html')


def provider_signup(request):
    return render(request, 'accounts/provider_signup.html')
def signup(request):
    return render(request, 'accounts/provider_signup.html')