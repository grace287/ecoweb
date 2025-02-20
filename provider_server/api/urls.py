from django.urls import path
from . import views

urlpatterns = [
    path('token/generate/', views.generate_admin_token, name='generate_token'),
    path('companies/pending/', views.pending_companies, name='pending_companies'),
    path('token/demand/', views.generate_demand_token, name='generate_demand_token'),
]
