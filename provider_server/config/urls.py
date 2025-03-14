from django.contrib import admin
from django.urls import path, include
from . import views
from .views import (
    provider_signup, 
    check_id_duplicate, 
    verify_business_number, 
    # ReceivedEstimatesAPIView, 
    # ReceivedEstimateDetailAPIView, 
    # respond_to_estimate, 
    ReceivedEstimateViewSet,
    toggle_star_estimate,
    #EstimateViewSet,
    # EstimateDetailViewSet,
    # estimate_detail  # 함수 기반 뷰
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

# Swagger 스키마 뷰 설정
schema_view = get_schema_view(
   openapi.Info(
      title="EcoMatch Provider API",
      default_version='v1',
      description="EcoMatch Provider 서버 API 문서입니다.",
      terms_of_service="https://www.ecomatch.com/terms/",
      contact=openapi.Contact(email="support@ecomatch.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

app_name = 'provider_server'

router = DefaultRouter()
router.register(r'estimates/received', ReceivedEstimateViewSet, basename='received_estimates')

urlpatterns = [
    path('', views.provider_login, name='provider_login'),
    path('admin/', admin.site.urls),

    # Swagger UI 및 문서 URL
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    path('signup/', provider_signup, name='provider_signup'),
    path('signup/pending/', views.provider_signup_pending, name='provider_signup_pending'),
    # path('signup/all/', views.provider_signup_all, name='provider_signup_all'),
    # path('companies/', views.get_all_companies, name='get_all_companies'),
    # ✅ JSON 데이터를 반환하는 API 엔드포인트 추가
    path('api/signup/pending/', views.api_provider_pending_list, name='api_provider_pending_list'),
    path('update_user-status/', views.update_user_status, name="update_user_status"),
    path('check-id/', check_id_duplicate, name='check_id'),
    path('verify-business-number/', verify_business_number, name='verify_business_number'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.provider_logout, name='provider_logout'),
    path('profile/', views.provider_profile, name='provider_profile'),

    
    # path('received_estimates/', views.received_estimates, name='received_estimates'),
    # path('estimates/received/', views.received_estimates, name='received_estimates_page'),
    # path('estimates/', views.provider_estimate_list, name='estimate_list'),
    # path('estimates/<int:pk>/', views.estimate_detail, name='estimate_detail'),
    # 받은 견적 목록 페이지 (HTML)
    path('estimate_list/', views.provider_estimate_list, name='provider_estimate_list'),
    path('estimate_list/estimates/received/', views.received_estimates, name='received-estimates'),
    path('estimate_list/estimates/received/<int:pk>/', views.estimate_detail, name='estimate-detail'),
    path('estimate_list/estimates/received/<int:pk>/respond/', views.provider_estimate_form, name='provider_estimate_form'),
    path('estimate_list/estimates/received/<int:pk>/view/', views.provider_estimate_form_view, name='provider_estimate_form_view'),
    path('estimate_list/estimates/received/<int:pk>/update/', views.provider_estimate_form_update, name='provider_estimate_form_update'),
    path('estimate_list/estimates/received/<int:pk>/send/', views.provider_send_estimate, name='provider_send_estimate'),

    path('estimate_list/estimates/check/<int:pk>/', views.check_estimate_exists, name='check_estimate_exists'),
    
    # path('provider_estimate_detail/', views.provider_estimate_detail, name='provider_estimate_detail'),    
    # path('estimate_detail/<int:pk>', views.provider_estimate_detail, name='provider_estimate_detail'),
    path('estimate_accept/<int:estimate_id>', views.provider_estimate_accept, name='provider_estimate_accept'),
    # path('estimate_reject/<int:pk>', views.provider_estimate_reject, name='provider_estimate_reject'),

    #path('provider_estimate_form/', views.provider_estimate_form, name='provider_estimate_form'),

    # JSON API 엔드포인트
    path('received_estimates/', views.received_estimates, name='received_estimates'),
    
    # API 엔드포인트
    path('api/', include(router.urls)),
    # path('api/estimates/received/<int:pk>/', ReceivedEstimateDetailAPIView.as_view(), name='received_estimate_detail_api'),
    # path('api/estimates/respond/', respond_to_estimate, name='respond_to_estimate'),
    path('api/estimates/received/', 
         ReceivedEstimateViewSet.as_view({'get': 'list'}), 
         name='received_estimates_api'),
    path('api/estimates/received/<int:estimate_id>/', 
         ReceivedEstimateViewSet.as_view({'get': 'retrieve'}),
         name='received_estimate_detail_api'),
    # path('api/estimates/respond/', respond_to_estimate, name='respond_to_estimate'),
    path('api/estimates/toggle-star/', toggle_star_estimate, name='toggle_star_estimate'),
    # path('api/estimates/detail/<int:pk>/', 
    #      EstimateDetailViewSet.as_view({'get': 'retrieve'}), 
    #      name='estimate-detail-view'),
    # path('api/estimates/<int:pk>/customer-info/', 
    #      EstimateDetailViewSet.as_view({'get': 'get_customer_info'}), 
    #      name='estimate-customer-info'),
    # path('api/estimates/<int:pk>/respond/', 
    #      EstimateDetailViewSet.as_view({'post': 'respond_to_estimate'}), 
    #      name='estimate-respond'),
    # path('estimates/<int:pk>/', 
    #      EstimateDetailViewSet.as_view({'get': 'retrieve'}), 
    #      name='estimate-detail'),
    # path('api/estimates/<int:pk>/', 
    #      EstimateDetailViewSet.as_view({'get': 'retrieve'}), 
    #      name='api-estimate-detail'),
]