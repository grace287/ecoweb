from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'estimates', views.EstimateViewSet)

urlpatterns = [
    path('', views.get_estimate_list, name='estimate-list'), # 견적 목록
    path('estimates/', views.get_estimate_list, name='estimate-list'), # 견적 목록
    path('received/', views.received_estimates, name='received-estimates'), # 받은 견적 목록
    path('estimates/received/', views.received_estimates, name='received-estimates'), # 받은 견적 목록
    path('estimates/<int:estimate_id>/', views.estimate_detail, name='estimate-detail'), # 견적 상세
    path('estimates/create/', views.create_estimate, name='create-estimate'), # 견적 생성
    
    
    # path('received_estimates/', views.received_estimates, name='received-estimates'), # 받은 견적 목록
    # path('<int:estimate_id>/', views.estimate_detail, name='estimate-detail'),
    
    path('measurement-locations/', views.get_measurement_locations, name='measurement-locations'),
    # path('request/submit/', views.estimate_request_submit, name='request_submit'),  # 견적 제출
    # path("success/", views.estimate_success, name="estimate_success"),  # 견적 요청 성공 페이지
    *router.urls
]