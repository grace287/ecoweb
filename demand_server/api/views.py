from django.shortcuts import render, redirect

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.conf import settings
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404
from users.models import DemandUser

def get_demand_user(request, user_id):
    """Demand 서버에서 특정 사용자 정보 제공"""
    user = get_object_or_404(DemandUser, id=user_id)
    
    data = {
        "id": user.id,
        "username": user.username,
        "company_name": user.company_name,
        "email": user.email,
        "business_registration_number": user.business_registration_number,
        "business_phone_number": user.business_phone_number,
        "contact_phone_number": user.contact_phone_number,
        "address": user.address,
        "address_detail": user.address_detail,
        "is_approved": user.is_approved
    }
    return JsonResponse(data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def generate_demand_token(request):
    """Demand 서버용 API 토큰 생성"""
    token, created = Token.objects.get_or_create(user=request.user)
    return Response({
        'token': token.key,
        'created': created
    })
@api_view(['POST'])
def switch_to_provider(request):
    if request.method == 'POST':
        user = request.user
        try:
            # 사용자 역할을 대행사로 변경하는 로직
            user.is_provider = True  # 예: is_provider 필드를 True로 설정
            user.save()
            
            return JsonResponse({'success': True, 'message': '대행사로 전환되었습니다.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': '잘못된 요청입니다.'}, status=400)



@login_required
def submit_estimate_request(request):
    if request.method == "POST":
        data = {
            "demand_user": request.user.username,
            "service_type": request.POST.get("service_type"),
            "description": request.POST.get("description"),
        }
        # headers = {"Authorization": f"Token {settings.COMMON_API_KEY}"}
        response = requests.post(f"{settings.COMMON_API_URL}/requests/", json=data, headers=headers)
        
        if response.status_code == 201:
            return redirect("estimate_requests")
        else:
            return render(request, "estimates/submit.html", {"error": "견적 요청 실패"})
    
    return render(request, "estimates/submit.html")

