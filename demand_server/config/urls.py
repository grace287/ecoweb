
from django.contrib import admin
from django.urls import path, include
from . import views
from .views import landing, main, login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing, name='landing'),
    path('main', main, name='main'),

    path('accounts/', include('allauth.urls')),

    path('login/', login, name='login'),
]
