from django.urls import path
from . import views

app_name = 'api'

def debug_view(request):
    from django.http import HttpResponse
    return HttpResponse("Debug view")

urlpatterns = [
    path('api/switch-to-provider/', views.switch_to_provider, name='switch_to_provider'),
    path('debug/', debug_view),  # 디버깅용 URL 패턴 추가
]
