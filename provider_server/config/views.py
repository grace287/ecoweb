from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from users.models import ProviderUser

ADMIN_API_URL = settings.ADMIN_API_URL
COMMON_API_URL = settings.COMMON_API_URL

def get_provider_user(request, provider_id):
    """Provider 서버에서 특정 사용자 정보 제공"""
    provider = get_object_or_404(ProviderUser, id=provider_id)
    
    data = {
        "id": provider.id,
        "username": provider.username,
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

@csrf_exempt
@require_http_methods(["GET", "POST"])
def provider_login(request):
    if request.method == "POST":
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            username = request.POST.get('username')
            password = request.POST.get('password')

            if not username or not password:
                return JsonResponse({'success': False, 'error': '아이디와 비밀번호를 입력해주세요.'})

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    # ✅ admin_panel 서버 API 호출하여 승인 상태 확인
                    admin_approval_api_url = f"{ADMIN_API_URL}/api/companies/{username}/"  # 예시 API 엔드포인트

                    try:
                        response = requests.get(admin_approval_api_url)
                        response.raise_for_status()  # HTTP 에러 체크
                        admin_data = response.json()

                        if admin_data.get('is_approved', False):  # API 응답에서 승인 여부 확인 (JSON 구조에 따라 키 변경)
                            login(request, user)  # ✅ 승인된 경우에만 로그인 허용
                            return JsonResponse({'success': True, 'redirect_url': '/dashboard/'})
                        else:
                            return JsonResponse({'success': False, 'error': '아직 관리자 승인 대기 중입니다. 승인 후 로그인해주세요.'}) # 승인 대기 중

                    except requests.exceptions.RequestException as e:
                        print(f"⚠️ admin_panel API 호출 실패: {e}") # 로깅
                        return JsonResponse({'success': False, 'error': '승인 상태 확인 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'}) # API 오류

                else: # user.is_active == False
                    return JsonResponse({'success': False, 'error': '계정이 비활성화되어 있습니다.'})
            else: # authenticate 실패
                return JsonResponse({'success': False, 'error': '아이디 또는 비밀번호가 올바르지 않습니다.'})

    # GET 요청 또는 일반 POST 요청 처리 (기존 코드 유지)
    return render(request, 'accounts/provider_login.html', {'csrf_token': get_token(request)})

@login_required
def provider_logout(request):
    logout(request)
    return redirect('provider_login')

@csrf_exempt
def provider_signup(request):
    """Provider 회원가입 API"""

    if request.method == "GET":
        """회원가입 폼 및 서비스 카테고리 목록 전달"""
        try:
            response = requests.get(f"{COMMON_API_URL}/services/service-categories/", timeout=5)
            response.raise_for_status()
            categories = response.json()
        except requests.RequestException as e:
            print("📌 서비스 카테고리 API 응답:", categories)  # 디버깅 로그 추가
            categories = []  # API 오류 시 빈 리스트 반환

        # ✅ JSON 직렬화하여 템플릿에 전달
        return render(request, "accounts/provider_signup.html", {"categories": json.dumps(categories)})

    elif request.method == "POST":
        """회원가입 데이터 처리"""
        try:
            # ✅ JSON 요청인지 확인
            content_type = request.content_type or ""
            if "application/json" in content_type.lower():
                if not request.body:
                    return JsonResponse({"success": False, "error": "요청 본문이 비어 있습니다."}, status=400)
                data = json.loads(request.body)  # JSON 데이터 파싱

            # ✅ Form 요청일 경우 (`application/x-www-form-urlencoded` 또는 `multipart/form-data`)
            else:
                data = request.POST.dict()  # Django에서 form-data를 dict로 변환

            print("📌 요청받은 데이터:", data)

            # 필수 필드 체크
            required_fields = ["username", "email", "password", "password_confirm", "company_name",
                               "business_registration_number", "business_phone_number", "address"]

            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return JsonResponse({"success": False, "error": f"필수 필드 누락: {', '.join(missing_fields)}"}, status=400)

            if data["password"] != data["password_confirm"]:
                return JsonResponse({"success": False, "error": "비밀번호가 일치하지 않습니다."}, status=400)

            # 중복 검사
            if ProviderUser.objects.filter(username=data["username"]).exists():
                return JsonResponse({"success": False, "error": "이미 사용 중인 아이디입니다."}, status=400)
            if ProviderUser.objects.filter(email=data["email"]).exists():
                return JsonResponse({"success": False, "error": "이미 사용 중인 이메일입니다."}, status=400)
            if ProviderUser.objects.filter(business_registration_number=data["business_registration_number"]).exists():
                return JsonResponse({"success": False, "error": "이미 등록된 사업자등록번호입니다."}, status=400)

            # ✅ 회원 생성
            user = ProviderUser.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                company_name=data["company_name"],
                business_phone_number=data["business_phone_number"],
                business_registration_number=data["business_registration_number"],
                address=data["address"],
                address_detail=data.get("address_detail", ""),
            )

            # ✅ 승인 대기 상태 설정
            user.is_active = False  # 가입 후 관리자 승인 전까지 로그인 불가
            user.save()

            # ✅ 회원가입 성공 후 승인 대기 페이지로 이동
            return JsonResponse({"success": True, "redirect_url": reverse("provider_signup_pending")}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "잘못된 JSON 데이터 형식입니다."}, status=400)

    return JsonResponse({"success": False, "error": "잘못된 요청 방식입니다."}, status=405)
def provider_signup_pending(request):
    return render(request, "accounts/provider_signup_pending.html")

@csrf_exempt
def update_user_status(request):
    """가입 승인 상태를 업데이트하는 API 뷰"""
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            username = data.get("username")
            is_approved = data.get("is_approved", False)

            provider = ProviderUser.objects.get(username=username)
            provider.is_active = is_approved  # ✅ 승인된 경우 로그인 가능하도록 변경
            provider.status = "approved" if is_approved else "pending"
            provider.save()

            return JsonResponse({"success": True, "message": "승인 상태가 업데이트되었습니다."}, status=200)
        except ProviderUser.DoesNotExist:
            return JsonResponse({"success": False, "error": "해당 사용자를 찾을 수 없습니다."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "잘못된 JSON 형식입니다."}, status=400)

    return JsonResponse({"success": False, "error": "잘못된 요청 방식입니다."}, status=405)

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