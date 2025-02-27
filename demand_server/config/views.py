from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json
import requests
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

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


def landing(request):
    return render(request, "landing.html")

def main(request):
    categories = [
        {'name': '전체보기', 'icon': ('img/main/category/all.png')},
        {'name': '실내공기질', 'icon': ('img/main/category/indoor-air.png')},
        {'name': '소음·진동', 'icon': ('img/main/category/noise-vibration.png')},
        {'name': '악취', 'icon': ('img/main/category/odor.png')},
        {'name': '수질', 'icon': ('img/main/category/water.png')},
        {'name': '대기', 'icon': ('img/main/category/air.png')},
        {'name': '중대재해', 'icon': ('img/main/category/major-disaster.png')},
        {'name': '사무실', 'icon': ('img/main/category/office.png')},
        {'name': 'ESG경영', 'icon': ('img/main/category/esg.png')},
    ]

    statistics = [
        {"value": "0", "unit": "만건 이상", "description": "누적 상담수", "image": ("status/multi-use.png"), "title": "지하주차장", "details": "(주)한**** 고객님 / 견적 상담중"},
        {"value": "0", "unit": "만건 이상", "description": "누적 측정수", "image": ("status/office.png"), "title": "사무실", "details": "(주)상**** 고객님 / 측정 및 분석중"},
        {"value": "35,000", "unit": "명 이상", "description": "누적 회원수", "image": ("status/analysis.png"), "title": "시료 분석", "details": "(주)일**** 고객님 / 분석 완료"},
    ]

    context = {
        "categories": categories,
        "statistics": statistics
    }

    return render(request, "main.html", context)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 사용자 인증
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/main'})
        else:
            return JsonResponse({'success': False, 'error': '아이디 또는 비밀번호가 올바르지 않습니다.'}, status=400)

    return render(request, "accounts/login_modal.html")

@require_POST
def signup(request):
    """회원가입 API"""
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

        # 필수값 검증
        if not username or not email or not password or not company_name or not business_phone_number or not address:
            return JsonResponse({"success": False, "error": "필수 정보를 모두 입력해주세요."}, status=400)

        # 비밀번호 일치 확인
        if password != password_confirm:
            return JsonResponse({"success": False, "error": "비밀번호가 일치하지 않습니다."}, status=400)

        # 중복 검사
        if DemandUser.objects.filter(username=username).exists():
            return JsonResponse({"success": False, "error": "이미 사용 중인 아이디입니다."}, status=400)
        if DemandUser.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "error": "이미 사용 중인 이메일입니다."}, status=400)

        # 사용자 생성
        user = DemandUser(
            username=username,
            email=email,
            company_name=company_name,
            business_phone_number=business_phone_number,
            address=address,
            address_detail=address_detail,
            recommend_id=recommend_id
        )
        user.set_password(password)  # 비밀번호 해싱
        user.save()

        auth_login(request, user)  # 자동 로그인
        return JsonResponse({"success": True, "redirect_url": "/signup_success/"}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "잘못된 JSON 데이터 형식입니다."}, status=400)

    except ValidationError as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

def signup_success(request):
    return render(request, "accounts/signup_success.html")

@require_POST
def check_id_duplicate(request):
    """아이디 중복 확인 API"""
    try:
        data = json.loads(request.body)
        username = data.get("username")

        if not username:
            return JsonResponse({"error": "아이디를 입력해주세요."}, status=400)

        is_duplicate = DemandUser.objects.filter(username=username).exists()
        return JsonResponse({"is_duplicate": is_duplicate})

    except json.JSONDecodeError:
        return JsonResponse({"error": "잘못된 JSON 데이터 형식입니다."}, status=400)


@require_POST
def check_email_duplicate(request):
    """이메일 중복 확인 API"""
    try:
        data = json.loads(request.body)
        email = data.get("email")

        if not email:
            return JsonResponse({"error": "이메일을 입력해주세요."}, status=400)

        is_duplicate = DemandUser.objects.filter(email=email).exists()
        return JsonResponse({"is_duplicate": is_duplicate})

    except json.JSONDecodeError:
        return JsonResponse({"error": "잘못된 JSON 데이터 형식입니다."}, status=400)


@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'info_edit':
            user.company_name = request.POST.get('company_name')
            user.business_phone_number = request.POST.get('business_phone_number')
            user.address = request.POST.get('address')
            user.address_detail = request.POST.get('address_detail')
            user.save()
            messages.success(request, "정보가 성공적으로 수정되었습니다.")
        elif form_type == 'customization':
            user.region = request.POST.get('region')
            user.industry = request.POST.get('industry')
            user.save()
            messages.success(request, "맞춤 설정이 성공적으로 저장되었습니다.")
        return redirect('profile')
    
    # GET 요청 시 필요한 추가 데이터(쿠폰, 거래내역, 찜한 대행사 등)도 context에 포함
    context = { 'user': user }
    return render(request, 'accounts/profile.html', context)


@login_required
def customization_update(request):
    if request.method == 'POST':
        # POST 데이터 처리 코드 작성 예시
        region = request.POST.get('region')
        industry = request.POST.get('industry')
        profile = request.user.profile
        profile.region = region
        profile.industry = industry
        profile.save()
        return redirect('profile') 

def logout(request):
    auth_logout(request)
    return redirect('main')


@login_required
def estimate_list(request):
    # 임시 데이터 리스트
    estimates = [
        {"id": 10, "type": "실내공기질 측정 외 1건", "location": "지하주차장 외 1곳", "status": "측정 진행중", "chats": 3, "quotes": 1, "request_date": "2025-01-05", "views": 15},
        {"id": 9, "type": "실내공기질 측정 외 1건", "location": "지하주차장 외 1곳", "status": "견적 요청중", "chats": 3, "quotes": 1, "request_date": "2025-01-05", "views": 15},
        {"id": 8, "type": "실내공기질 측정 외 1건", "location": "지하주차장 외 1곳", "status": "견적 수락완료", "chats": 3, "quotes": 1, "request_date": "2025-01-05", "views": 15},
        {"id": 7, "type": "실내공기질 측정 외 1건", "location": "지하주차장 외 1곳", "status": "견적 수락완료", "chats": 3, "quotes": 1, "request_date": "2025-01-05", "views": 15},
        {"id": 6, "type": "실내공기질 측정 외 1건", "location": "지하주차장 외 1곳", "status": "견적 요청중", "chats": 3, "quotes": 1, "request_date": "2025-01-05", "views": 15},
        {"id": 5, "type": "실내공기질 측정 외 1건", "location": "지하주차장 외 1곳", "status": "견적 수락완료", "chats": 3, "quotes": 1, "request_date": "2025-01-05", "views": 15},
        {"id": 4, "type": "실내공기질 측정 외 1건", "location": "지하주차장 외 1곳", "status": "견적 요청중", "chats": 3, "quotes": 1, "request_date": "2025-01-05", "views": 15},
        {"id": 3, "type": "실내공기질 측정 외 1건", "location": "지하주차장 외 1곳", "status": "견적 요청중", "chats": 3, "quotes": 1, "request_date": "2025-01-05", "views": 15},
        {"id": 2, "type": "실내공기질 측정 외 1건", "location": "지하주차장 외 1곳", "status": "견적 수락완료", "chats": 3, "quotes": 1, "request_date": "2025-01-05", "views": 15},
        {"id": 1, "type": "중대재해처벌법 컨설팅", "location": "사무실 외 1곳", "status": "견적 요청중", "chats": 3, "quotes": 1, "request_date": "2025-01-04", "views": 7},
    ]

    # 페이지네이션 적용 (한 페이지당 5개 항목)
    paginator = Paginator(estimates, 5)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    """견적 목록 조회"""
    try:
        # Common API 서버에서 견적 목록 조회
        response = requests.get(
            f"{settings.COMMON_API_URL}/api/estimates/",
            params={'demand_user_id': request.user.id},
            headers={'Authorization': f'Token {settings.COMMON_API_TOKEN}'}
        )
        estimates = response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"Error: {e}")
        estimates = []
        
    return render(request, 'demand/estimates/demand_estimate_list.html', {
        'estimates': estimates
    })


@login_required
# def estimate_detail(request, estimate_id):
#     """견적 상세 조회"""
#     try:
#         # Common API 서버에서 견적 상세 조회
#         response = requests.get(
#             f"{settings.COMMON_API_URL}/api/estimates/{estimate_id}/",
#             headers={'Authorization': f'Token {settings.COMMON_API_TOKEN}'}
#         )
#         if response.status_code == 200:
#             estimate = response.json()
#         else:
#             return redirect('estimate_list')
#     except Exception as e:
#         print(f"Error: {e}")
#         return redirect('estimate_list')
        
#     return render(request, 'demand/estimates/demand_estimate_detail.html', {
#         'estimate': estimate
#     })


def estimate_detail(request):
    # 임시 데이터
    estimate = {
        "title": "(주)ABC 고객님.",
        "request_date": "2025.01.05(화), 15:21",
        "client_name": "(주)ABC 고객님",
        "client_phone": "02-123-4567",
        "client_fax": "02-3456-7890",
        "client_email": "abc@naver.com",
        "location": "서울특별시 강남구 테헤란로 129(역삼동)",
        "estimate_date": "2025.01.13",
        "company_phone": "02-123-4567",
        "company_fax": "02-3456-7890",
        "company_email": "air@naver.com",
        "note": "측정완료 후 보고서를 제공해드립니다.",
        "measurements": [
            {"type": "실내공기질 측정(BPM 10, PM 2.5, 라돈 등)", "maintain": 2, "recommend": 4, "unit_price": 450000, "subtotal": 2700000},
            {"type": "소음·진동 측정(작업환경측정, 층간소음 등)", "maintain": 2, "recommend": 1, "unit_price": 450000, "subtotal": 1350000},
        ],
        "supply_price": 4050000,
        "discount": 405000,
        "vat": 364500,
        "total": 4009500,
        "company_name": "(주)측정하는업체",
        "signature_date": "2025.01.13"
    }
    return render(request, "demand/estimates/demand_estimate_detail.html", {"estimate": estimate})

def estimate_accept(request):
    # 임시 데이터
    estimate = {
        "title": "(주)ABC 고객님.",
        "request_date": "2025.01.05(화), 15:21",
        "client_name": "(주)ABC 고객님",
        "client_phone": "02-123-4567",
        "client_fax": "02-3456-7890",
        "client_email": "abc@naver.com",
        "location": "서울특별시 강남구 테헤란로 129(역삼동)",
        "estimate_date": "2025.01.13",
        "company_phone": "02-123-4567",
        "company_fax": "02-3456-7890",
        "company_email": "air@naver.com",
        "note": "측정완료 후 보고서를 제공해드립니다.",
        "measurements": [
            {"type": "실내공기질 측정(BPM 10, PM 2.5, 라돈 등)", "maintain": 2, "recommend": 4, "unit_price": 450000, "subtotal": 2700000},
            {"type": "소음·진동 측정(작업환경측정, 층간소음 등)", "maintain": 2, "recommend": 1, "unit_price": 450000, "subtotal": 1350000},
        ],
        "supply_price": 4050000,
        "discount": 405000,
        "vat": 364500,
        "total": 4009500,
        "company_name": "(주)측정하는업체",
        "signature_date": "2025.01.13"
    }
    return render(request, 'demand/estimates/demand_estimate_accept.html',{"estimate": estimate})

def estimate_request_guest(request):
    """비회원 견적 요청"""
    if request.user.is_authenticated:
        return redirect('estimate_request_form')
        
    if request.method == 'POST':
        try:
            # Common API 서버로 게스트 견적 요청 전송
            response = requests.post(
                f"{settings.COMMON_API_URL}/api/estimates/",
                json=request.POST.dict(),
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 201:
                return JsonResponse({
                    'success': True,
                    'message': '견적 요청이 완료되었습니다. 로그인 후 확인해주세요.'
                })
            return JsonResponse({'success': False, 'error': '견적 요청 실패'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
            
    return render(request, 'demand/estimates/estimate_request_guest.html')

@login_required
def estimate_request_form(request):
    """회원 견적 요청"""
    if request.method == 'POST':
        try:
            # Common API 서버로 견적 요청 전송
            response = requests.post(
                f"{settings.COMMON_API_URL}/api/estimates/",
                json={
                    **request.POST.dict(),
                    'demand_user_id': request.user.id
                },
                headers={
                    'Authorization': f'Token {settings.COMMON_API_TOKEN}',
                    'Content-Type': 'application/json'
                }
            )
            if response.status_code == 201:
                return JsonResponse({'success': True, 'redirect_url': '/estimates/list/'})
            return JsonResponse({'success': False, 'error': '견적 요청 실패'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
            
    return render(request, 'demand/estimates/estimate_request_form.html')



@login_required
def chat(request):
    return render(request, 'demand/estimates/estimate_request_guest.html')


def chat_estimate(request):
    service_type = request.POST.get('service_type', '미선택')  # POST 데이터에서 가져옴
    location_type = request.POST.get('location_type', '미선택')
    selected_date = request.POST.get('selected_date', '미선택')
    selected_address = request.POST.get('selected_address', '미입력')
    # ...
    context = {
        'service_type': service_type,
        'location_type': location_type,
        'selected_date': selected_date,
        'selected_address': selected_address,
        # ...
    }
    return render(request, 'demand/estimates/estimate_request_guest.html', context)