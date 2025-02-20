from django.urls import path
from . import views

urlpatterns = [
    path('token/generate/', views.generate_admin_token, name='generate_token'),
]
