from django.contrib import admin
from django.urls import path, include
from . import views
from .views import provider_signup, check_id_duplicate, verify_business_number

app_name = 'provider_server'

urlpatterns = [
    path('', views.provider_login, name='login'),
    path('admin/', admin.site.urls),

    path('login/', views.provider_login, name='provider_login'),

    path('signup/', provider_signup, name='provider_signup'),
    path('signup/pending/', views.provider_signup_pending, name='provider_signup_pending'),
    path('check-id/', check_id_duplicate, name='check_id'),
    path('verify-business-number/', verify_business_number, name='verify_business_number'),
    
    path('dashboard/', views.provider_dashboard, name='dashboard'),
    path('logout/', views.provider_logout, name='provider_logout'),
    path('profile/', views.provider_profile, name='provider_profile'),

]