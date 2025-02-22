from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import views
from .views import landing, main, login, signup, signup_success
from .views import check_id_duplicate, check_email_duplicate

app_name = 'demand_server'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing, name='landing'),
    path('main', main, name='main'),
    path('api/', include('api.urls')),

    # Accounts
    path('accounts/', include('allauth.urls')),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('signup/success/', views.signup_success, name='signup_success'),
    path("check-id/", check_id_duplicate, name="check_id"),
    path("check-email-duplicate/", check_email_duplicate, name="check_email_duplicate"),
    path("profile", views.profile, name="profile"),

    # Estimates
    path('estimates_request_guest/', views.estimate_request_guest, name='estimate_request_guest'),
    path('estimates_request_form/', views.estimate_request_form, name='estimate_request_form'),
    path('estimates_list/', views.estimate_list, name='estimate_list'),
    path('estimate_detail/', views.estimate_detail, name='estimate_detail'),
    path('estimate_accept/', views.estimate_accept, name='estimate_accept'),
    # path('estimates/detail/<int:estimate_id>/', views.estimate_detail, name='estimate_detail'),

    # Chat
    path('chat/', views.chat, name='chat'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)