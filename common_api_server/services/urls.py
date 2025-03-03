from django.urls import path
from .views import service_category_list, get_measurement_locations
from . import views

urlpatterns = [
    path("service-categories/", service_category_list, name="service_category_list"),
    path('measurement-locations/', get_measurement_locations, name='measurement-locations'),
]
