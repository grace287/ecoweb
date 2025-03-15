from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import views
from .views import landing, main, login, signup, signup_success
from .views import check_id_duplicate, check_email_duplicate # 이 뷰를 import해야 합니다
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

app_name = 'demand_server'

from rest_framework.decorators import api_view

# Swagger 스키마 뷰 설정
schema_view = get_schema_view(
   openapi.Info(
      title="Demand Server API",
      default_version='v1',
      description="Demand 서버의 견적 관련 API 문서",
      terms_of_service="https://www.example.com/policies/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

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
    path("check-username-duplicate/", check_id_duplicate, name="check_id"),
    path("check-email-duplicate/", check_email_duplicate, name="check_email_duplicate"),
    path("profile", views.profile, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/customization/update/", views.customization_update, name="customization_update"),

    # Estimates
    path('estimates_request_guest/', views.estimate_request_guest, name='estimate_request_guest'),
    path('estimates/request/', views.estimate_request_form, name='estimate_request_form'),
    # path('estimates/request/guest/', views.estimate_request_guest, name='estimate_request_guest'),
    # path('estimates_request_form/', views.estimate_request_form, name='estimate_request_form'),
    # path('estimates/create/', views.create_estimate, name='create_estimate'),
    path('estimates_list/', views.estimate_list, name='estimate_list'),
    path('estimates/<int:estimate_id>/', views.received_estimate_detail, name='estimate_detail'),
    # path('estimate_accept/', views.estimate_accept, name='estimate_accept'),
    # path('estimates/detail/<int:estimate_id>/', views.estimate_detail, name='estimate_detail'),

    # Chat
    path('chat/', views.chat, name='chat'),

    # Swagger 문서 URL 추가
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)