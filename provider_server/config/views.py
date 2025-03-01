from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login as auth_login
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from users.models import ProviderUser, Attachment, ServiceCategory


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

@login_required
def provider_logout(request):
    logout(request)
    return redirect('provider_login')

@csrf_exempt
@require_http_methods(["GET", "POST"])
def provider_signup(request):
    """회원가입 API"""
    if request.method == "GET":
        categories = ServiceCategory.objects.all()
        return JsonResponse({"categories": categories}, status=200)

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            password_confirm = data.get("password_confirm")
            company_name = data.get("company_name")
            business_registration_number = data.get("business_registration_number")
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
            if ProviderUser.objects.filter(business_registration_number=business_registration_number).exists():
                return JsonResponse({"success": False, "error": "이미 등록된 사업자등록번호입니다."}, status=400)

            user = ProviderUser(
                username=username,
                email=email,
                company_name=company_name,
                business_registration_number=business_registration_number,
                business_phone_number=business_phone_number,
                address=address,
                address_detail=address_detail,
                recommend_id=recommend_id
            )
            # ✅ 선택한 서비스 카테고리 저장 (API에서 가져온 코드만 저장)
            user.set_password(password)
            user.save()

            

            # 선택한 서비스 카테고리 연결
            if service_category_ids:
                categories = ServiceCategory.objects.filter(id__in=service_category_ids)
                user.service_category.set(categories)

            # 관리자 서버에 회원가입 요청 전송
            admin_api_url = f"{settings.ADMIN_API_URL}/api/companies/"
            company_data = {
                "username": username,
                "email": email,
                "company_name": company_name,
                "business_registration_number": business_registration_number,
                "business_number": business_registration_number,
                "status": "pending"
            }

            try:
                response = requests.post(
                    admin_api_url,
                    json=company_data,
                    headers={"Authorization": f"Bearer {settings.ADMIN_API_KEY}"}
                )

                if response.status_code == 201:
                    return redirect("provider_signup_pending")
                else:
                    return render(request, "accounts/provider_signup.html", {
                        "error": "회원가입 처리 중 오류가 발생했습니다.",
                        "categories": ServiceCategory.objects.all()
                    })

            except requests.RequestException:
                return render(request, "accounts/provider_signup.html", {
                    "error": "서버 통신 오류가 발생했습니다.",
                    "categories": ServiceCategory.objects.all()
                })

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "잘못된 JSON 데이터 형식입니다."}, status=400)

        except Exception as e:
            return render(request, "accounts/provider_signup.html", {
                "error": str(e),
                "categories": ServiceCategory.objects.all()
            })

        return JsonResponse({"success": True, "user_id": user.id}, status=201)

    return JsonResponse({"success": False, "error": "잘못된 요청 방식입니다."}, status=405)

def provider_signup_pending(request):
    return render(request, "accounts/provider_signup_pending.html")

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

def provider_estimate_accept(request, pk):
    # 수락 처리 로직 추가
    # 예: estimate.status = 'accepted'
    # estimate.save()
    return render(request, 'provider/estimates/provider_estimate_detail.html')


def provider_estimate_form(request):
    return render(request, 'provider/estimates/provider_estimate_form.html')