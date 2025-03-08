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
from users.models import ProviderUser

ADMIN_PANEL_URL = settings.ADMIN_PANEL_URL
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

@csrf_exempt
def provider_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 슈퍼유저는 바로 로그인 가능
            if user.is_superuser:
                login(request, user)
                return JsonResponse({'success': True, 'redirect_url': '/dashboard/'})

            # 일반 사용자는 승인 상태 확인
            if user.is_active:
                login(request, user)
                return JsonResponse({'success': True, 'redirect_url': '/dashboard/'})
            else:
                return JsonResponse({
                    'success': False, 
                    'error': '아직 관리자 승인 대기 중입니다. 승인 후 로그인해주세요.'
                })
        else:
            return JsonResponse({
                'success': False, 
                'error': '아이디 또는 비밀번호가 올바르지 않습니다.'
            })

    return render(request, 'accounts/provider_login.html')


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
            # user = ProviderUser.objects.create_user(
            #     username=data["username"],
            #     email=data["email"],
            #     password=data["password"],
            #     company_name=data["company_name"],
            #     business_phone_number=data["business_phone_number"],
            #     business_registration_number=data["business_registration_number"],
            #     address=data["address"],
            #     address_detail=data.get("address_detail", ""),
            # )

            # 가입 요청 생성 (승인 대기 상태)
            provider_user = ProviderUser.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                company_name=data["company_name"],
                business_registration_number=data["business_registration_number"],
                business_phone_number=data["business_phone_number"],
                address=data["address"],
                address_detail=data.get("address_detail", ""),
                is_active=False,  # 관리자 승인 전까지 비활성화
                is_approved=False  # 승인 대기 상태
            )

            # ✅ 승인 대기 상태 설정
            ProviderUser.is_active = False  # 가입 후 관리자 승인 전까지 로그인 불가
            ProviderUser.save()

            # Admin 서버에 가입 요청 동기화
            # ✅ Admin 서버에 가입 요청 동기화
            admin_sync_url = f"{ADMIN_API_URL}/sync-provider-signup/"
            sync_data = {
                "username": provider_user.username,
                "email": provider_user.email,
                "company_name": provider_user.company_name,
                "business_registration_number": provider_user.business_registration_number,
                "business_phone_number": provider_user.business_phone_number,
            }

            try:
                response = requests.post(admin_sync_url, json=sync_data)
                if response.status_code != 200:
                    print(f"⚠️ Admin 서버 동기화 실패: {response.text}")  # Log error
            except requests.RequestException as e:
                print(f"⚠️ Admin 서버 동기화 중 네트워크 오류: {e}")

            # ✅ 회원가입 성공 후 승인 대기 페이지로 이동
            return redirect('provider_signup_pending')

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "잘못된 JSON 데이터 형식입니다."}, status=400)

    return JsonResponse({"success": False, "error": "잘못된 요청 방식입니다."}, status=405)

    

def provider_signup_pending(request):
    
    """회원가입 승인 대기 페이지"""
    if request.method == "GET":
        pending_users = ProviderUser.objects.filter(is_approved=False).values(
            "username", "company_name", "email", "business_registration_number"
        )
        return JsonResponse({"requests": list(pending_users)}, safe=False)

    return JsonResponse({"error": "잘못된 요청 방식입니다."}, status=405)


def api_provider_pending_list(request):
    """승인 대기 중인 Provider 목록을 JSON으로 반환"""
    pending_users = ProviderUser.objects.filter(is_active=False).values(
        "username", "company_name", "email", "business_registration_number"
    )
    return JsonResponse(list(pending_users), safe=False)

@csrf_exempt
@login_required
def update_user_status(request):
    """✅ 가입 승인 상태를 업데이트하는 API 뷰 (관리자 전용)"""
    if not request.user.is_superuser:
        return JsonResponse({"success": False, "error": "관리자만 승인할 수 있습니다."}, status=403)

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            username = data.get("username")
            is_approved = data.get("is_approved", False)

            provider = ProviderUser.objects.get(username=username)
            provider.is_active = is_approved  # 승인된 경우 로그인 가능
            provider.is_approved = is_approved
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

@login_required
def get_estimate_list(request):
    """견적 리스트 조회 API"""
    try:
        # 현재 로그인한 Provider의 ID 가져오기
        provider_user_id = request.user.id

        # URL 쿼리 파라미터 구성
        params = {
            "provider_user_id": provider_user_id,
            "status": request.GET.get("status", ""),
            "search": request.GET.get("search", "")
        }

        # 공통 API 서버에서 받은 견적 요청 조회
        common_api_url = f"{settings.COMMON_API_URL}/estimates/received/"
        
        # requests 라이브러리 사용
        response = requests.get(
            common_api_url, 
            params=params, 
            timeout=10,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        # 응답 상태 코드 확인
        if response.status_code != 200:
            return JsonResponse({
                'estimates': [],
                'error': f'API 요청 실패: {response.status_code} - {response.text}'
            }, status=response.status_code)

        # JSON 파싱
        estimates_data = response.json()

        # JSON 응답
        return JsonResponse({
            'estimates': estimates_data.get('estimates', [])
        }, status=200)
    
    except requests.RequestException as e:
        return JsonResponse({
            'estimates': [],
            'error': f'네트워크 오류: {str(e)}'
        }, status=500)


@login_required
def estimate_detail(request, estimate_id):
    try:
        # 공통 API 서버에서 견적서 상세 정보 조회
        api_url = f"{settings.COMMON_API_URL}/estimates/{estimate_id}/"
        
        # 디버깅을 위한 로깅 추가
        print(f"📝 견적 상세 조회 API URL: {api_url}")

        response = requests.get(
            api_url, 
            timeout=10,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        # 응답 상태 코드 및 내용 로깅
        print(f"📝 응답 상태 코드: {response.status_code}")
        print(f"📝 응답 내용: {response.text}")

        # 응답 상태 코드 확인
        if response.status_code != 200:
            return JsonResponse({
                'error': '견적서 조회 중 오류가 발생했습니다.',
                'details': response.text
            }, status=response.status_code)
        
        # JSON 파싱
        estimate_data = response.json()
        
        # 컨텍스트 생성
        context = {
            'estimate': estimate_data,
            'estimate_id': estimate_id
        }
        
        return render(request, 'provider/estimates/estimate_detail.html', context)
    
    except requests.RequestException as e:
        # 네트워크 오류 처리
        print(f"🚨 견적서 조회 중 네트워크 오류: {e}")
        return JsonResponse({
            'error': '견적서 조회 중 네트워크 오류가 발생했습니다.',
            'details': str(e)
        }, status=500)

def provider_estimate_accept(request, pk):
    # 수락 처리 로직 추가
    # 예: estimate.status = 'accepted'
    # estimate.save()
    return render(request, 'provider/estimates/provider_estimate_detail.html')


def provider_estimate_form(request):
    return render(request, 'provider/estimates/provider_estimate_form.html')

@csrf_exempt
def notify_estimate_request(request):
    """✅ Provider 서버 - 견적 요청 알림 수신"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            estimate_id = data.get("estimate_id")

            if not estimate_id:
                return JsonResponse({"error": "견적 ID가 필요합니다."}, status=400)

            print(f"📌 새로운 견적 요청: #{estimate_id}")
            return JsonResponse({"success": True}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)

    return JsonResponse({"error": "잘못된 요청 방식입니다."}, status=405)




@csrf_exempt
def received_estimates(request):
    try:
        # 현재 로그인한 Provider의 ID 가져오기
        provider_user_id = request.user.id

        # URL 쿼리 파라미터 구성
        params = {
            "provider_user_id": provider_user_id,
            "status": request.GET.get("status", ""),
            "search": request.GET.get("search", "")
        }

        context = {
        "common_api_url": settings.COMMON_API_URL,  # 템플릿에 API URL 전달
    }

        # 공통 API 서버에서 받은 견적 요청 조회
        common_api_url = f"{settings.COMMON_API_URL}/estimates/received/"
        
        # 디버깅을 위한 상세 로깅 추가
        print(f"📝 전체 API URL: {common_api_url}")
        print(f"📝 COMMON_API_URL: {settings.COMMON_API_URL}")
        print(f"📝 요청 파라미터: {params}")

        # requests 라이브러리 사용 시 추가 디버깅
        response = requests.get(
            common_api_url, 
            params=params, 
            timeout=10,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        # 전체 응답 내용 출력
        print(f"📝 응답 상태 코드: {response.status_code}")
        print(f"📝 응답 헤더: {response.headers}")
        print(f"📝 응답 내용: {response.text}")

        # 응답 상태 코드 및 내용 확인
        if response.status_code != 200:
            return render(request, 'provider/estimates/provider_estimate_list.html', {
                'estimates': [],
                'error': f'API 요청 실패: {response.status_code} - {response.text}'
            })

        try:
            estimates_data = response.json()
        except json.JSONDecodeError as e:
            return render(request, 'provider/estimates/provider_estimate_list.html', {
                'estimates': [],
                'error': f'JSON 파싱 오류: {str(e)} - 응답 내용: {response.text}'
            })

        # 템플릿 렌더링
        context = {
            'estimates': estimates_data.get('estimates', []),
            'list_type': 'received'
        }
        
        return render(request, 'provider/estimates/provider_estimate_list.html', context)
    
    except requests.RequestException as e:
        return render(request, 'provider/estimates/provider_estimate_list.html', {
            'estimates': [],
            'error': f'네트워크 오류: {str(e)}'
        })



@csrf_exempt
def respond_to_estimate(request, estimate_id):
    """✅ Provider 서버 - 견적 응답"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            provider_user_id = data.get("provider_user_id")
            response_details = data.get("response_details")

            if not provider_user_id or not response_details:
                return JsonResponse({"error": "필수 입력값이 누락되었습니다."}, status=400)

            # ✅ 공통 API 서버로 견적 응답 전송
            api_url = f"{settings.COMMON_API_URL}/estimates/{estimate_id}/respond/"
            response = requests.post(api_url, json=data)

            if response.status_code == 201:
                return JsonResponse(response.json(), status=201)
            return JsonResponse(response.json(), status=response.status_code)

        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)

    return JsonResponse({"error": "잘못된 요청 방식입니다."}, status=405)

def provider_pending_list(request):
    """승인 대기 중인 Provider 목록을 JSON으로 반환"""
    pending_users = ProviderUser.objects.filter(is_active=False).values(
        "username", "company_name", "email", "business_registration_number"
    )
    return JsonResponse(list(pending_users), safe=False)

def provider_signup_all(request):
    """모든 회사 정보를 반환하는 API"""
    companies = ProviderUser.objects.all().values(
        'username', 
        'company_name', 
        'business_registration_number', 
        'email',
        'business_phone_number',
        'is_active',
        'is_approved',
        'created_at'
    )
    return JsonResponse(list(companies), safe=False)
    

def get_all_companies(request):
    """모든 회사 정보를 반환하는 API"""
    companies = ProviderUser.objects.all().values(
        'username', 
        'company_name', 
        'business_registration_number', 
        'email', 
        'business_phone_number', 
        'is_active',
        'is_approved',
        'created_at'
    )
    return JsonResponse(list(companies), safe=False)

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
