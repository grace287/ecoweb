from django.urls import path
from .views import service_category_list
from . import views

urlpatterns = [
    path("service-categories/", views.service_category_list, name="service_category_list"),
]
