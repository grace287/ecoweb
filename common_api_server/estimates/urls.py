from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'estimates', views.EstimateViewSet)

urlpatterns = [
    # provider 견적 목록 조회
    path('estimates/', views.get_estimate_list, name='estimate-list'),
    
    # provider 받은 견적 목록 조회
    path('estimates/received/', views.received_estimates, name='received-estimates'),
    
    # provider 견적 상세 조회
    path('estimates/received/<int:estimate_id>/', views.estimate_detail, name='estimate-detail'),
    
    # demand 견적 생성
    path('estimates/create/', views.create_estimate, name='create-estimate'),
    
    # 측정 장소 조회
    path('measurement-locations/', views.get_measurement_locations, name='measurement-locations'),

    # 견적 저장 또는 업데이트
    path('estimates/<int:pk>/create_or_update/', views.create_or_update_estimate, name='create_or_update_estimate'),


    # provider 견적발송 조회
    path('estimates/<int:pk>/send/', views.estimate_send, name='estimate_send'),

    # 수요자 견적 목록 조회 (보낸 요청 + 받은 견적)
    path('estimates/demand/list/', views.demand_estimate_list, name='demand_estimate_list'),
    
    # 수요자 견적 상세 조회
    path('estimates/demand/request/<int:pk>/', views.demand_request_detail, name='demand_request_detail'),
    path('estimates/demand/response/<int:pk>/', views.demand_response_detail, name='demand_response_detail'),
    # ViewSet 라우트 추가
    *router.urls
]