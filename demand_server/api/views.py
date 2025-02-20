from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.conf import settings
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])
@permission_classes([IsAdminUser])
def generate_demand_token(request):
    """Demand 서버용 API 토큰 생성"""
    token, created = Token.objects.get_or_create(user=request.user)
    return Response({
        'token': token.key,
        'created': created
    })

@csrf_exempt
@api_view(['POST'])
def switch_to_provider(request):
    if request.method == 'POST':
        # 전환 로직을 여기에 작성하세요
        return JsonResponse({'redirect_url': 'http://localhost:8001'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

