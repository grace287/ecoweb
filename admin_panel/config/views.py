from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from users.models import Company, AdminUser  # Company 모델로 변경
from django.db.models import Q, Count
import requests
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login

@login_required
def approve_provider_requests(request):
    """
    대행사 가입 승인 요청을 처리하는 뷰
    - POST: 승인 처리 및 provider_server에 알림
    - GET: 승인 대기 중인 대행사 목록 표시
    """
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        company = Company.objects.get(id=user_id)
        
        # 승인 처리
        company.status = 'approved'
        company.approved_at = timezone.now()
        company.approved_by = request.user
        company.save()

        # provider_server에 승인 상태 업데이트
        api_url = "http://provider-server.com/api/update_user_status/"
        data = {
            'username': company.username,
            'is_approved': True
        }

        try:
            response = requests.post(api_url, json=data)
            if response.status_code == 200:
                return redirect("admin_approve_requests")
            else:
                return JsonResponse({"error": "Provider 서버 업데이트 실패"}, status=500)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)

    # 승인 대기 중인 대행사 목록 조회
    pending_providers = Company.objects.filter(
        status='pending',
        user_type='provider'
    ).select_related('approved_by')
    
    return render(request, "admin_panel/approve_requests.html", {
        "pending_providers": pending_providers
    })


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
    companies = CompanyUser.objects.all().order_by('-created_at')
    return render(request, 'company/list.html', {'companies': companies})

@login_required
def company_detail(request, pk):
    company = CompanyUser.objects.get(pk=pk)
    return render(request, 'company/detail.html', {'company': company})

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