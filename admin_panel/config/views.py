from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from users.models import Company, AdminUser  # Company 모델로 변경
from django.db.models import Q, Count
import requests
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.core.exceptions import ValidationError

import logging

DEMAND_API_URL = settings.DEMAND_API_URL
PROVIDER_API_URL = settings.PROVIDER_API_URL
COMMON_API_URL = settings.COMMON_API_URL

logger = logging.getLogger(__name__)

@login_required
def demand_user_list(request):
    """Demand 유저 목록을 외부 API에서 가져옴"""
    try:
        response = requests.get(f"{settings.DEMAND_API_URL}/demand-users/", timeout=5)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
        demand_users = response.json()
    except requests.RequestException as e:
        logger.error(f"⚠️ Demand Server API 요청 실패: {e}")
        demand_users = []

    return JsonResponse({"demand_users": demand_users}, status=200)

@login_required
def approve_provider_requests(request):
    """
    대행사 가입 승인 요청을 처리하는 뷰
    - POST: 승인 처리 및 provider_server에 알림
    - GET: 승인 대기 중인 대행사 목록 표시
    """
    
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        
        # ✅ 예외 처리: 존재하지 않는 ID 요청 방지
        try:
            company = Company.objects.get(id=user_id)
        except Company.DoesNotExist:
            return JsonResponse({"error": "해당 ID의 회사가 존재하지 않습니다."}, status=404)

        # 승인 처리
        company.status = "approved"
        company.approved_at = timezone.now()
        company.approved_by = request.user
        company.save()

        # provider_server에 승인 상태 업데이트
        api_url = f"{settings.PROVIDER_API_URL}/update_user_status/"
        data = {
            "username": company.username,
            "is_approved": True
        }

        try:
            response = requests.post(api_url, json=data, timeout=5)
            response.raise_for_status()  # ✅ HTTP 에러 발생 시 예외 처리
            return redirect("admin_approve_requests")
        except requests.RequestException as e:
            logger.error(f"⚠️ Provider 서버 업데이트 실패: {e}")
            return JsonResponse({"error": "Provider 서버 업데이트 실패"}, status=500)

    # ✅ provider_server에서 가입 요청 데이터 가져오기
    try:
        response = requests.get(
            f"{settings.PROVIDER_API_URL}/signup/pending/",
            timeout=5
        )

        response.raise_for_status()  # ✅ HTTP 에러 발생 시 예외 처리
        provider_companies = response.json()  # ✅ API 응답이 JSON이 아닐 경우 예외 발생 가능
    except requests.RequestException as e:
        logger.error(f"⚠️ API 요청 실패: {e}")
        provider_companies = []

    # ✅ 로컬 DB에서 가입 요청 목록 가져오기
    local_companies = Company.objects.filter(status="pending")

    # ✅ 중복 제거: 사업자번호 기준 병합 (KeyError 방지)
    company_dict = {company.get("business_registration_number", ""): company for company in provider_companies}

    for company in local_companies:
        brn = company.business_registration_number  # business_registration_number
        if brn and brn not in company_dict:
            company_dict[brn] = {
                "id": company.id,
                "company_name": company.company_name,
                "user_type": company.user_type,
                "business_registration_number": brn,
                "email": company.email,
                "business_phone_number": company.business_phone_number,
                "created_at": company.created_at.isoformat(),
                "source": "local"
            }

    pending_companies = list(company_dict.values())

    return render(request, "admin_panel/approve_requests.html", {"pending_companies": pending_companies})

@login_required
def dashboard(request):
    """관리자 대시보드 뷰"""
    
    # ✅ 안전한 쿼리로 통계 데이터 가져오기
    try:
        stats = {
            'total': Company.objects.count(),
            'provider': Company.objects.filter(user_type='provider').count(),
            'demand': Company.objects.filter(user_type='demand').count(),
            'pending': Company.objects.filter(status='pending').count()
        }
        
        # ✅ 최근 가입 신청 업체 목록
        recent_companies = Company.objects.all().order_by('-created_at')[:10]

    except Exception as e:
        # 오류 발생 시 안전한 메시지 출력
        stats = {'error': str(e)}
        recent_companies = []

    context = {
        'stats': stats,
        'recent_companies': recent_companies
    }

    return render(request, 'dashboard/dashboard.html', context)


@login_required
def company_list(request):
    """업체 리스트 페이지"""
    demand_users = DemandUser.objects.all()  # 모든 DemandUser 조회
    provider_users = ProviderUser.objects.filter(status="pending")  # 승인 대기 중인 ProviderUser 조회

    context = {
        "demand_users": demand_users,
        "provider_users": provider_users,
    }
    companies = Company.objects.all().order_by('-created_at')
    return render(request, 'dashboard/company_list.html', {'companies': companies})

@login_required
def company_detail(request, pk):
    company = Company.objects.get(pk=pk)
    return render(request, 'dashboard/company_detail.html', {'company': company})

def admin_login(request):
    """관리자 로그인 뷰"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            
            if remember_me:
                # 세션 만료 기간을 2주로 설정
                request.session.set_expiry(1209600)
            
            return redirect('dashboard')
        else:
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
    
    return render(request, 'accounts/login.html')

@login_required
def logout(request):
    """로그아웃 뷰"""
    auth_logout(request)
    return redirect('login')


@login_required
def profile(request):
    """관리자 프로필 뷰"""
    return render(request, 'accounts/profile.html')


def pending_companies(request):
    return JsonResponse({"error": "This is a test response"}, status=200)


def fetch_provider_users():
    """Provider 서버에서 승인 대기 중인 유저 목록 가져오기"""
    try:
        url = f"{settings.PROVIDER_API_URL}/signup/pending/"
        response = requests.get(url, headers={"Content-Type": "application/json"}, timeout=5)

        if response.status_code == 200:
            return response.json()
        else:
            return []
    except requests.RequestException as e:
        print(f"⚠️ Provider 서버 API 요청 실패: {e}")
        return []

def provider_users_view(request):
    """Django 뷰에서 Provider 서버의 유저 데이터를 JSON으로 반환"""
    provider_users = fetch_provider_users()
    return JsonResponse({"provider_users": provider_users})