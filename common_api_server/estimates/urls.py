from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('estimates/create/', views.create_estimate, name='create-estimate'),
    path('<int:estimate_id>/', views.estimate_detail, name='estimate-detail'),
    path('estimates/', views.get_estimate_list, name='estimate-list'),
    path('measurement-locations/', views.get_measurement_locations, name='measurement-locations'),
    # path('request/guest/', views.estimate_request_guest, name='estimate_request_guest'),  # 비회원용
    # path('request/form/', views.estimate_request_form, name='request_form'),  # 회원용
    # path('request/submit/', views.estimate_request_submit, name='request_submit'),  # 견적 제출
    # path("success/", views.estimate_success, name="estimate_success"),  # 견적 요청 성공 페이지
]
