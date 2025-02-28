# provider_server/users/views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ProviderUser
import json
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import ProviderUser, ServiceCategory

@api_view(['GET'])
def get_provider_user_info(request, user_id):
    """유저 ID로 provider 유저 정보를 조회하는 API"""
    user = get_object_or_404(ProviderUser, id=user_id)
    return JsonResponse({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "company_name": user.company_name
    })

def sync_service_categories_view(request):
    """공통 API 서버에서 `ServiceCategory` 데이터를 동기화하는 뷰"""
    ServiceCategory.sync_service_categories()
    return JsonResponse({"message": "ServiceCategory 동기화 완료"})

@csrf_exempt
def signup(request):
    """회원가입 API"""
    if request.method == "GET":
        # ✅ 공통 API 서버에서 서비스 카테고리 가져와서 회원가입 폼에 전달
        categories = ServiceCategory.objects.all()
        return render(request, "accounts/signup.html", {"categories": categories})

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            password_confirm = data.get("password_confirm")
            company_name = data.get("company_name")
            business_phone_number = data.get("business_phone_number")
            address = data.get("address")
            address_detail = data.get("address_detail")
            recommend_id = data.get("recommend_id")
            service_category_ids = data.get("service_category_ids", [])

            if not username or not email or not password or not company_name or not business_phone_number or not address:
                return JsonResponse({"success": False, "error": "필수 정보를 모두 입력해주세요."}, status=400)

            if password != password_confirm:
                return JsonResponse({"success": False, "error": "비밀번호가 일치하지 않습니다."}, status=400)

            if ProviderUser.objects.filter(username=username).exists():
                return JsonResponse({"success": False, "error": "이미 사용 중인 아이디입니다."}, status=400)
            if ProviderUser.objects.filter(email=email).exists():
                return JsonResponse({"success": False, "error": "이미 사용 중인 이메일입니다."}, status=400)

            user = ProviderUser(
                username=username,
                email=email,
                company_name=company_name,
                business_phone_number=business_phone_number,
                address=address,
                address_detail=address_detail,
                recommend_id=recommend_id
            )
            user.set_password(password)
            user.save()

            # ✅ 선택한 서비스 카테고리 연결
            if service_category_ids:
                categories = ServiceCategory.objects.filter(id__in=service_category_ids)
                user.service_category.set(categories)

            auth_login(request, user)
            return JsonResponse({"success": True, "redirect_url": "/signup_success/"}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "잘못된 JSON 데이터 형식입니다."}, status=400)

    return JsonResponse({"success": False, "error": "잘못된 요청 방식입니다."}, status=405)