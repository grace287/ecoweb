from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger 스키마 뷰 설정
schema_view = get_schema_view(
   openapi.Info(
      title="EcoMatch Estimates API",
      default_version='v1',
      description="""
      EcoMatch 견적 관리 API 문서입니다.
      
      ## 주요 기능
      - 견적 생성
      - 견적 목록 조회
      - 견적 상세 조회
      - 견적 상태 업데이트
      
      ## 인증
      - 세션 인증 사용
      - 로그인 필요
      """,
      terms_of_service="https://www.ecomatch.com/terms/",
      contact=openapi.Contact(email="support@ecomatch.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', views.home, name="home"),
    path('admin/', admin.site.urls),
    path('estimates/', include("estimates.urls")),
    path('services/', include("services.urls")),
    path('api/', include('api.urls')),
    # path('auth/', include('authentication.urls')),  # authentications -> authentication
    # Swagger UI 및 문서 URL
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
