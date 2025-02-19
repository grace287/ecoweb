
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

    # ✅ provider_server 네임스페이스 추가 (대행사 서버 연결)
    path('accounts/', include('allauth.urls')),

    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('signup/', views.signup, name='signup'),
    path('signup/success/', views.signup_success, name='signup_success'),
    path("check-id/", check_id_duplicate, name="check_id"),
    path("check-email-duplicate/", check_email_duplicate, name="check_email_duplicate"),

    path("profile", views.profile, name="profile"),
]