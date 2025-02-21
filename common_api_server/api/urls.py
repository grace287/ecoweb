from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # path('estimates/', views.EstimateListCreateView.as_view(), name='estimate-list'),
    # path('estimates/<str:estimate_number>/', views.EstimateDetailView.as_view(), name='estimate-detail'),
    # path('estimates/<str:estimate_number>/respond/', views.EstimateResponseView.as_view(), name='estimate-respond'),
    # path('estimates/<str:estimate_number>/approve/', views.EstimateApproveView.as_view(), name='estimate-approve'),
    # path('estimates/<str:estimate_number>/reject/', views.EstimateRejectView.as_view(), name='estimate-reject'),
]