from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'payments', views.PaymentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
