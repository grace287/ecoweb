from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login as auth_login
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate  # 올바른 경로로 수정
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token # 견적 요청 모델

from users.models import ProviderUser, Attachment


def get_provider_user(request, provider_id):
    """Provider 서버에서 특정 사용자 정보 제공"""
    provider = get_object_or_404(ProviderUser, id=provider_id)
    
    data = {
        "id": provider.id,
        "username": provider.username,
        "company_name": provider.company_name,
        "email": provider.email,
        "business_registration_number": provider.business_registration_number,
        "business_phone_number": provider.business_phone_number,
        "consultation_phone_number": provider.consultation_phone_number,
        "address": provider.address,
        "address_detail": provider.address_detail,
        "is_approved": provider.is_approved,
        "service_category": list(provider.service_category.values_list("name", flat=True))
    }
    return JsonResponse(data)

def main(request):
    return render(request, 'main.html') 

@require_http_methods(["GET", "POST"])
def provider_login(request):
    if request.method == "POST":
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            if not username or not password:
                return JsonResponse({
                    'success': False,
                    'error': '아이디와 비밀번호를 입력해주세요.'
                })
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return JsonResponse({
                        'success': True,
                        'redirect_url': '/dashboard/'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': '계정이 비활성화되어 있습니다.'
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'error': '아이디 또는 비밀번호가 올바르지 않습니다.'
                })
                
    # GET 요청이거나 일반 POST 요청인 경우
    return render(request, 'accounts/provider_login.html', {
        'csrf_token': get_token(request)
    })

# def login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
        
#         # 관리자 서버에서 승인 상태 확인
#         admin_api_url = f"{settings.ADMIN_API_URL}/api/companies/check-status/"
        
#         if user is not None:
#             # admin_panel에서 승인 여부 호가인
#             approval_status = requests.get(f"{settings.ADMIN_PANEL_API_URL}/companies/{user.id}/")
#             if approval_status.json().get('status') == 'approved':
#                 login(request, user)
#                 return redirect('provider_dashboard')
#             else:
#                 return render(request, 'accounts/provider_login.html', {'error': '관리자의 승인이 필요합니다.'})
    
#         try:
#             response = requests.post(
#                 admin_api_url,
#                 json={'username': username},
#                 headers={'Authorization': f'Bearer {settings.ADMIN_API_KEY}'}
#             )
            
#             if response.status_code == 200:
#                 status_data = response.json()
#                 if status_data['status'] != 'approved':
#                     return render(request, 'accounts/provider_login.html', {
#                         'error': '관리자 승인 대기 중입니다.'
#                     })
                    
#                 # 승인된 경우 로그인 처리
#                 user = authenticate(request, username=username, password=password)
#                 if user is not None:
#                     auth_login(request, user)
#                     return redirect('provider_dashboard')
                    
#             return render(request, 'accounts/provider_login.html', {
#                 'error': '아이디 또는 비밀번호가 올바르지 않습니다.'
#             })
            
#         except requests.RequestException:
#             return render(request, 'accounts/provider_login.html', {
#                 'error': '서버 통신 오류가 발생했습니다.'
#             })

#     return render(request, 'accounts/provider_login.html')

@login_required
@csrf_exempt
def provider_logout(request):
    return redirect('provider_login')

@csrf_exempt
def provider_signup(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            company_name = request.POST.get('company_name')
            business_registration_number = request.POST.get('business_registration_number')
            business_phone_number = request.POST.get('business_phone_number')
            consulting_phone_number = request.POST.get('consulting_phone_number')
            address = request.POST.get('address')
            address_detail = request.POST.get('address_detail')
            service_category = request.POST.get('service_category')
            attachments = request.FILES.getlist('attachment')

            # 기본 유효성 검사
            if not all([username, email, password, company_name, 
                       business_registration_number, business_phone_number, address]):
                return render(request, 'accounts/provider_signup.html', {
                    'error': '필수 항목을 모두 입력해주세요.',
                    'service_categories': ServiceCategory.objects.all()
                })

            # 중복 체크
            if ProviderUser.objects.filter(username=username).exists():
                return render(request, 'accounts/provider_signup.html', {
                    'error': '이미 사용 중인 아이디입니다.',
                    'service_categories': ServiceCategory.objects.all()
                })

            if ProviderUser.objects.filter(email=email).exists():
                return render(request, 'accounts/provider_signup.html', {
                    'error': '이미 사용 중인 이메일입니다.',
                    'service_categories': ServiceCategory.objects.all()
                })

            if ProviderUser.objects.filter(business_registration_number=business_registration_number).exists():
                return render(request, 'accounts/provider_signup.html', {
                    'error': '이미 등록된 사업자등록번호입니다.',
                    'service_categories': ServiceCategory.objects.all()
                })

            # 사용자 생성
            user = ProviderUser(
                username=username,
                email=email,
                password=make_password(password),
                company_name=company_name,
                business_registration_number=business_registration_number,
                business_phone_number=business_phone_number,
                consultation_phone_number=consulting_phone_number,
                address=address,
                address_detail=address_detail,
            )
            user.save()

            # 서비스 카테고리 설정
            if service_category:
                category_codes = service_category.split(',')
                categories = ServiceCategory.objects.filter(category_code__in=category_codes)
                user.service_category.set(categories)

            # 첨부파일 저장
            for attachment in attachments:
                Attachment.objects.create(user=user, file=attachment)

            # 관리자 서버에 회원가입 요청 전송
            admin_api_url = f"{settings.ADMIN_API_URL}/api/companies/"
            
            company_data = {
                'username': username,
                'email': email,
                'company_name': company_name,
                'business_number': business_registration_number,
                'user_type': 'provider',
                'status': 'pending'
            }
            
            try:
                response = requests.post(
                    admin_api_url,
                    json=company_data,
                    headers={'Authorization': f'Bearer {settings.ADMIN_API_KEY}'}
                )
                
                if response.status_code == 201:
                    return redirect('provider_signup_pending')
                else:
                    return render(request, 'accounts/provider_signup.html', {
                        'error': '회원가입 처리 중 오류가 발생했습니다.'
                    })
                    
            except requests.RequestException:
                return render(request, 'accounts/provider_signup.html', {
                    'error': '서버 통신 오류가 발생했습니다.'
                })

        except Exception as e:
            return render(request, 'accounts/provider_signup.html', {
                'error': str(e),
                'service_categories': ServiceCategory.objects.all()
            })

    else:
        return render(request, 'accounts/provider_signup.html', {
            'service_categories': ServiceCategory.objects.all()
        })

def signup(request):
    return render(request, 'accounts/provider_signup.html')

def provider_signup_pending(request):
    return render(request, 'accounts/provider_signup_pending.html')

# admin_panel_api.py
def send_signup_request(company_data):
    """admin_panel 서버에 업체 가입 요청을 전송"""
    api_url = f"{settings.ADMIN_PANEL_API_URL}/companies/"
    response = requests.post(api_url, json=company_data)

    return response.json()

@csrf_exempt
def check_id_duplicate(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("id")

            if not user_id:
                return JsonResponse({"error": "아이디를 입력해주세요."}, status=400)

            is_duplicate = ProviderUser.objects.filter(username=user_id).exists()
            return JsonResponse({"is_duplicate": is_duplicate})

        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 데이터 형식입니다."}, status=400)

    return JsonResponse({"error": "잘못된 요청"}, status=400)

@csrf_exempt
def verify_business_number(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            business_number = data.get("business_number")

            if not business_number:
                return JsonResponse({"error": "사업자등록번호를 입력해주세요."}, status=400)

            # 사업자등록번호 검증 로직 추가
            # 예시: 사업자등록번호 검증 API 호출
            is_valid = True  # 검증 결과 예시

            return JsonResponse({"is_valid": is_valid})

        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 데이터 형식입니다."}, status=400)

    return JsonResponse({"error": "잘못된 요청"}, status=400)


# @login_required
# def provider_dashboard(request):
#     context = {
#         'status_data': {
#             'in_progress': {
#                 'count': 5,
#                 'label': '진행중',
#                 'color': '#2563eb'
#             },
#             'recruiting': {
#                 'count': 8,
#                 'label': '모집',
#                 'color': '#059669'
#             },
#             'meeting': {
#                 'count': 3,
#                 'label': '미팅',
#                 'color': '#7C3AED'
#             }
#         },
#         'progress_data': [
#             {
#                 'label': '전체 진행률',
#                 'value': 65,
#                 'color': '#2563eb'
#             },
#             {
#                 'label': '가입 현황',
#                 'value': 80,
#                 'color': '#059669'
#             },
#             {
#                 'label': '견적 완료율',
#                 'value': 45,
#                 'color': '#7C3AED'
#             }
#         ],
#         'financial_data': {
#             'today_settlement': 456789,
#             'total_revenue': 123456789,
#             'monthly_growth': 15.7,
#             'pending_payments': 3
#         }
#     }
#     return render(request, 'provider/provider_dashboard.html', context)

@login_required
def dashboard(request):
    status_data = {
        "in_progress": {"label": "진행중", "count": 2, "color": "#2563eb"},
        "requested": {"label": "요청", "count": 4, "color": "#374151"},
        "completed": {"label": "완료", "count": 1, "color": "#10b981"},
    }

    progress_data = [
        {"label": "측정 완료율", "value": 80, "color": "#2563eb"},
        {"label": "견적 완료율", "value": 75, "color": "#22c55e"},
        {"label": "채팅 완료율", "value": 80, "color": "#fbbf24"},
        {"label": "정산 완료율", "value": 40, "color": "#ec4899"},
    ]

    financial_data = {
        "today_settlement": 123456,
        "total_revenue": 100000000,
        "monthly_growth": 5,
        "pending_payments": 3,
    }

    return render(request, "provider/dashboard.html", {
        "status_data": status_data,
        "progress_data": progress_data,
        "financial_data": financial_data,
    })

    
@login_required
def provider_profile(request):
    if not request.user.is_authenticated:
        return redirect('provider_login')
        
    context = {
        'user': request.user,
        'service_categories': request.user.service_category.all(),
    }
    return render(request, 'accounts/profile.html', context)

def provider_estimate_list(request): # 필요에 따라 필터 적용
    return render(request, 'provider/estimates/provider_estimate_list.html')


def provider_estimate_detail(request):
    return render(request, 'provider/estimates/provider_estimate_detail.html')

# def provider_estimate_detail(request, pk):
#     return render(request, 'provider/estimates/provider_estimate_detail.html')

def provider_estimate_accept(request, pk):
    # 수락 처리 로직 추가
    # 예: estimate.status = 'accepted'
    # estimate.save()
    return render(request, 'provider/estimates/provider_estimate_detail.html')


def provider_estimate_form(request):
    return render(request, 'provider/estimates/provider_estimate_form.html')