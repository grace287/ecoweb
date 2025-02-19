from django.contrib import admin
from django.urls import path,include
from . import views

app_name = 'provider_server'

urlpatterns = [
    path('', views.provider_login, name='login'),
    path('admin/', admin.site.urls),

    path('signup/', views.signup, name='signup'),

    path('signup/', views.provider_signup, name='signup'),  # 회원가입
      # 대행사 로그인
    
]