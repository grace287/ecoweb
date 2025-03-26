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
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth import login as auth_login, get_backends
from rest_framework.decorators import api_view
from users.models import DemandUser
import logging
from django.urls import reverse

ADMIN_PANEL_URL = settings.ADMIN_PANEL_URL
COMMON_API_URL = settings.COMMON_API_URL

logger = logging.getLogger(__name__)

def get_demand_user(request, user_id):
    """Demand 서버에서 특정 사용자 정보 제공"""
    user = get_object_or_404(DemandUser, id=user_id)
    
    data = {
        "id": user.id,
        "username": user.username,
        "company_name": user.company_name,
        "email": user.email,
        "business_phone_number": user.business_phone_number,
        "contact_phone_number": user.contact_phone_number,
        "address": user.address,
        "address_detail": user.address_detail,
        "is_approved": user.is_approved
    }
    return JsonResponse(data)


def get_demand_users(request):
    """Demand User 목록 반환"""
    demand_users = list(DemandUser.objects.values("id", "username", "email", "company_name", "created_at"))
    return JsonResponse({"demand_users": demand_users}, safe=False)


# 로그인 시 랜딩페이지말고 main으로 리다이렉트.
def landing(request):
    if request.user.is_authenticated:
        return redirect('main')
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

@api_view(['GET', 'POST'])
@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')


        # 사용자 인증
        user = authenticate(request, username=username, password=password)

        if user is not None:
            user.backend = get_backends()[0].__class__.__module__ + "." + get_backends()[0].__class__.__name__
            auth_login(request, user)

            # ✅ 세션 유지
            request.session.set_expiry(0)  # 브라우저 닫으면 세션 만료 (기본값)
            request.session.modified = True  # 세션 갱신

            # ✅ 로그인 성공 시 메인 페이지로 리다이렉트
            next_url = request.GET.get('next', '/main')
            return JsonResponse({'success': True, 'redirect_url': next_url})

        else:
            return JsonResponse({'success': False, 'error': '아이디 또는 비밀번호가 올바르지 않습니다.'}, status=400)

    return render(request, "accounts/login_modal.html")

@api_view(['GET'])
def logout(request):
    auth_logout(request)
    return redirect('main')

@api_view(['GET'])
@csrf_protect
def signup(request):
    """회원가입 API"""
    """회원가입 API"""
    if request.method == "GET":
        return render(request, "accounts/signup.html")  # ✅ HTML 페이지 렌더링 추가

    if request.method == "POST":
        try:
            body_unicode = request.body.decode('utf-8')  # ✅ JSON 데이터 변환
            data = json.loads(body_unicode)

            print("📌 요청받은 데이터:", data)  # ✅ 요청 데이터 출력

            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            password_confirm = data.get("password_confirm")
            company_name = data.get("company_name")
            business_phone_number = data.get("business_phone_number")
            address = data.get("address")
            address_detail = data.get("address_detail")
            recommend_id = data.get("recommend_id")

            # ✅ 필수 필드 확인
            required_fields = ["username", "email", "password", "company_name", "business_phone_number", "address"]
            missing_fields = [field for field in required_fields if not data.get(field) or data.get(field).strip() == ""]


            if missing_fields:
                return JsonResponse({
                    "success": False,
                    "error": f"다음 필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
                }, status=400)

            if password != password_confirm:
                return JsonResponse({"success": False, "error": "비밀번호가 일치하지 않습니다."}, status=400)

            # ✅ 중복 검사 개선
            if DemandUser.objects.filter(username=username).exists():
                return JsonResponse({
                    "success": False,
                    "error": f"❌ '{username}' 아이디는 이미 사용 중입니다. 다른 아이디를 입력해주세요."
                }, status=400)

            if DemandUser.objects.filter(email=email).exists():
                return JsonResponse({
                    "success": False,
                    "error": f"❌ '{email}' 이메일은 이미 사용 중입니다. 다른 이메일을 입력해주세요."
                }, status=400)
            
            # ✅ 새로운 사용자 생성
            user = DemandUser(
                username=username,
                email=email,
                company_name=company_name,
                business_phone_number=business_phone_number,
                address=address,
                address_detail=address_detail,
                recommend_id=recommend_id,
                is_active=True,  # 자동 활성화
                is_approved=True  # 자동 승인
            )
            user.set_password(password)
            user.save()

            return JsonResponse({"success": True, "redirect_url": "/signup/success/"}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "잘못된 JSON 데이터 형식입니다."}, status=400)
        except Exception as e:
            print("📌 서버 오류:", str(e))  # ✅ 디버깅 로그 추가
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "잘못된 요청 방식입니다."}, status=405)

@api_view(['GET'])
def signup_success(request):     
    return render(request, "accounts/signup_success.html")

@csrf_exempt
def check_username_duplicate(request):
    """아이디 중복 확인 API"""
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data.get("username")

            if not username:
                return JsonResponse({"success": False, "error": "아이디를 입력해주세요."}, status=400)

            is_duplicate = DemandUser.objects.filter(username=username).exists()

            return JsonResponse({"success": True, "is_duplicate": is_duplicate})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "잘못된 JSON 데이터 형식입니다."}, status=400)
    return JsonResponse({"success": False, "error": "잘못된 요청 방식입니다."}, status=405)


@csrf_exempt
def check_email_duplicate(request):
    """이메일 중복 확인 API"""
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get("email")

            if not email:
                return JsonResponse({"success": False, "error": "이메일을 입력해주세요."}, status=400)

            is_duplicate = DemandUser.objects.filter(email=email).exists()

            return JsonResponse({"success": True, "is_duplicate": is_duplicate})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "잘못된 JSON 데이터 형식입니다."}, status=400)
    return JsonResponse({"success": False, "error": "잘못된 요청 방식입니다."}, status=405)

@csrf_exempt
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


@csrf_exempt
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
def profile_edit(request):
     return render(request, 'accounts/profile_edit.html')


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



    
@api_view(['GET', 'POST'])
@csrf_exempt
def estimate_request_guest(request):
    """비회원 견적 요청"""
    if request.user.is_authenticated:
        return redirect('estimate_request_form')
        
    if request.method == 'POST':
        try:
            # Common API 서버로 게스트 견적 요청 전송
            response = requests.post(
                f"{settings.COMMON_API_URL}/estimates/",
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

@api_view(['GET', 'POST'])
@login_required
def estimate_request_form(request):
    """견적 요청 폼 및 처리"""
    if request.method == 'GET':
        try:
            # 세션 유효성 검사
            if not request.user.is_authenticated:
                return redirect('login')
                
            # 세션 갱신
            request.session.modified = True

            # API 엔드포인트 설정
            api_endpoints = {
                'categories_url': f"{settings.COMMON_API_URL}/services/service-categories/",
                'locations_url': f"{settings.COMMON_API_URL}/estimates/measurement-locations/",
                'create_estimate_url': f"{settings.COMMON_API_URL}/estimates/estimates/create/"
            }
            
            # Common API 서버 요청
            categories_response = requests.get(
                api_endpoints['categories_url'],
                headers={'Accept': 'application/json'}
            )
            locations_response = requests.get(
                api_endpoints['locations_url'],
                headers={'Accept': 'application/json'}
            )
            
            # API 응답 검증
            if categories_response.status_code != 200:
                logger.error(f"카테고리 조회 실패: {categories_response.status_code} - {categories_response.text}")
                categories = []
            else:
                categories = categories_response.json()

            if locations_response.status_code != 200:
                logger.error(f"측정 장소 조회 실패: {locations_response.status_code} - {locations_response.text}")
                locations = []
            else:
                locations = locations_response.json()
            
            # 컨텍스트에 API 엔드포인트 정보 추가
            context = {
                'categories': categories,
                'locations': locations,
                'user': request.user,
                'api_endpoints': api_endpoints,  # API 엔드포인트 정보 전달
                'COMMON_API_URL': settings.COMMON_API_URL,
                'api_config': {
                    'baseUrl': settings.COMMON_API_URL,
                    'endpoints': {
                        'categories': '/services/service-categories/',
                        'locations': '/estimates/measurement-locations/',
                        'createEstimate': '/estimates/estimates/create/'
                    }
                }
            }
            
            return render(request, 'demand/estimates/estimate_request_form.html', context)
        
        except requests.RequestException as e:
            logger.error(f"API 요청 중 오류 발생: {str(e)}")
            return JsonResponse({
                'error': '서비스 정보를 불러오는 중 오류가 발생했습니다.',
                'details': str(e)
            }, status=500)
            
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # 견적 요청 데이터 준비
            estimate_data = {
                'demand_user_id': request.user.id,
                'service_category_codes': data.get('service_category_codes', []),
                'measurement_location_id': data.get('measurement_location_id'),
                'address': data.get('address'),
                'preferred_schedule': data.get('preferred_schedule'),
                'contact_info': {
                    'name': request.user.username,
                    'phone': request.user.contact_phone_number,
                    'email': request.user.email
                }
            }
            
            # Common API 서버로 견적 요청 전송
            response = requests.post(
                f"{settings.COMMON_API_URL}/estimates/estimates/create/",
                json=estimate_data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            if response.status_code == 201:
                result = response.json()
                return JsonResponse({
                    'success': True,
                    'estimate_id': result['estimate_id'],
                    'message': '견적 요청이 성공적으로 생성되었습니다.'
                }, status=201)
            else:
                logger.error(f"견적 생성 실패: {response.status_code} - {response.text}")
                return JsonResponse({
                    'success': False,
                    'error': '견적 요청 처리 중 오류가 발생했습니다.'
                }, status=response.status_code)

        except json.JSONDecodeError:
            return JsonResponse({'error': '잘못된 요청 데이터입니다.'}, status=400)
        except Exception as e:
            logger.error(f"견적 요청 처리 중 오류 발생: {str(e)}")
            return JsonResponse({'error': '서버 오류가 발생했습니다.'}, status=500)




@api_view(['GET'])
@csrf_exempt
def approve_estimate(request, estimate_id):
    """견적 승인 & 결제 요청 (Demand 서버)"""
    if request.method == "POST":
        try:
            estimate = Estimate.objects.get(id=estimate_id)
            estimate.status = "APPROVED"  # 견적 승인 처리
            estimate.save()

            # 결제 서버에 결제 요청
            payment_data = {
                "estimate_id": estimate.id,
                "amount": estimate.total_amount,
                "user_id": estimate.demand_user_id,
            }
            payment_response = requests.post(f"{settings.PAYMENT_SERVER_URL}/pay/", json=payment_data)

            return JsonResponse({"success": True, "payment_response": payment_response.json()}, status=200)

        except Estimate.DoesNotExist:
            return JsonResponse({"error": "견적을 찾을 수 없습니다."}, status=404)

    return JsonResponse({"error": "잘못된 요청 방식입니다."}, status=405)

@api_view(['GET'])
@csrf_exempt
def request_estimate(request):
    """✅ Demand 사용자가 견적 요청"""
    if request.method == "GET":
        """회원가입 폼 및 서비스 카테고리 목록 전달"""
        try:
            response = requests.get(f"{COMMON_API_URL}/services/service-categories/", timeout=5)
            response = requests.get(f"{COMMON_API_URL}/estimates/measurement-locations/", timeout=5)
            response.raise_for_status()
            categories = response.json()
        except requests.RequestException as e:
            print("📌 서비스 카테고리 API 응답:", categories)  # 디버깅 로그 추가
            categories = []  # API 오류 시 빈 리스트 반환

        # ✅ JSON 직렬화하여 템플릿에 전달
        return render(request, "demand/estimates/estimate_request_form.html", {"categories": json.dumps(categories)})
    
    elif request.method == "POST":
        try:
            # 🔹 요청 데이터 파싱
            data = json.loads(request.body)
            demand_user_id = data.get("demand_user_id")
            provider_user_id = data.get("provider_user_id")
            measurement_location_id = data.get("measurement_location_id")
            category_code = data.get("service_category_code")
            address = data.get("address")

            # 🔹 필수 데이터 확인
            if not all([demand_user_id, measurement_location_id, category_code, address]):
                return JsonResponse({"error": "필수 입력값이 누락되었습니다."}, status=400)

            # 🔹 서비스 카테고리 검증
            service_category = ServiceCategory.objects.filter(category_code=category_code).first()
            if not service_category:
                return JsonResponse({"error": "잘못된 서비스 카테고리입니다."}, status=400)

            # 🔹 측정 장소 검증
            measurement_location = MeasurementLocation.objects.filter(id=measurement_location_id).first()
            if not measurement_location:
                return JsonResponse({"error": "잘못된 측정 장소입니다."}, status=400)

            # ✅ 견적 요청 생성
            estimate = Estimate.objects.create(
                demand_user_id=demand_user_id,
                provider_user_id=provider_user_id,
                service_category=service_category,
                measurement_location=measurement_location,
                address=address,
                status="REQUEST",
            )

            # ✅ Provider 서버에 견적 요청 알림 전송
            provider_api_url = f"{settings.PROVIDER_API_URL}/estimates/received/"
            requests.post(provider_api_url, json={"estimate_id": estimate.id})

            return JsonResponse({"success": True, "estimate_id": estimate.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)

    return JsonResponse({"error": "잘못된 요청 방식입니다."}, status=405)


@api_view(['GET'])
@csrf_exempt
def pay_estimate(request):
    """Demand 사용자가 견적 승인 후 결제 요청"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            estimate_id = data.get("estimate_id")

            # ✅ 견적서 가져오기
            try:
                estimate = Estimate.objects.get(id=estimate_id)
            except Estimate.DoesNotExist:
                return JsonResponse({"error": "존재하지 않는 견적입니다."}, status=404)

            # ✅ 결제 서버에 결제 요청
            payment_api_url = f"{settings.PAYMENT_SERVER_URL}/api/payments/process/"
            payment_response = requests.post(payment_api_url, json={"estimate_id": estimate.id, "amount": estimate.total_amount})

            if payment_response.status_code == 200:
                estimate.status = "PAID"
                estimate.save()
                return JsonResponse({"success": True, "message": "결제 완료"}, status=200)
            else:
                return JsonResponse({"error": "결제 실패"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)

    return JsonResponse({"error": "잘못된 요청 방식입니다."}, status=405)


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

@api_view(['GET'])
@csrf_exempt
def request_payment(request, estimate_id):
    """견적 결제 요청"""
    try:
        # Payment API 서버에 결제 생성 요청
        response = requests.post(
            f"{settings.PAYMENT_API_URL}/api/payments/",
            json={
                'estimate_id': estimate_id,
                'payment_method': request.data.get('payment_method')
            }
        )
        
        if response.status_code == 201:
            payment_data = response.json()
            # 결제 처리 요청
            process_response = requests.post(
                f"{settings.PAYMENT_API_URL}/api/payments/{payment_data['id']}/process_payment/"
            )
            
            if process_response.status_code == 200:
                return JsonResponse({
                    "success": True,
                    "message": "결제가 성공적으로 처리되었습니다."
                })
            
        return JsonResponse({
            "success": False,
            "error": "결제 처리 중 오류가 발생했습니다."
        }, status=400)
        
    except requests.RequestException as e:
        return JsonResponse({
            "success": False,
            "error": f"결제 서버 통신 중 오류 발생: {str(e)}"
        }, status=500)
    

from django.http import JsonResponse

# demand/views.py

@api_view(['GET'])
@login_required
def estimate_list(request):
    """견적 요청 + 받은 견적 목록 조회"""
    try:
        status = request.GET.get('status') or None  # 빈 문자열이면 None
        search = request.GET.get('search', '')
        page = request.GET.get('page', '1')

        common_api_url = f"{settings.COMMON_API_URL}/estimates/estimates/demand/list/"
        params = {
            "demand_user_id": request.user.id,
            "search": search,
            "page": page,
            "page_size": 10
        }

        if status:
            params["status"] = status

        logger.info(f"[LOAD_ESTIMATES] 요청: {common_api_url} | params: {params}")

        response = requests.get(
            common_api_url,
            params=params,
            timeout=10,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        if response.status_code != 200:
            logger.error(f"[LOAD_ESTIMATES] API Error: {response.status_code} - {response.text}")
            return JsonResponse({
                'error': 'API 요청 실패',
                'code': response.status_code,
                'text': response.text
            }, status=response.status_code)

        estimates_data = response.json()
        logger.debug(f"[LOAD_ESTIMATES] 수신 데이터: {estimates_data}")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(estimates_data, status=200)

        status_counts = {
            'REQUEST': sum(1 for e in estimates_data.get('estimates', []) if e.get('status') == 'REQUEST'),
            'RESPONSE': sum(1 for e in estimates_data.get('estimates', []) if e.get('status') == 'RESPONSE'),
            'APPROVED': sum(1 for e in estimates_data.get('estimates', []) if e.get('status') == 'APPROVED'),
            'REJECTED': sum(1 for e in estimates_data.get('estimates', []) if e.get('status') == 'REJECTED')
        }

        context = {
            'estimates': estimates_data.get('estimates', []),
            'total_count': estimates_data.get('total_count', 0),
            'status_counts': status_counts,
            'has_next': estimates_data.get('has_next', False),
            'has_previous': estimates_data.get('has_previous', False),
            'current_page': int(page),
            'status': status,
            'search': search
        }

        logger.info(f"[LOAD_ESTIMATES] 페이지 렌더링: 견적 수={len(context['estimates'])}")
        return render(request, 'demand/estimates/demand_estimate_list.html', context)

    except requests.RequestException as e:
        logger.exception(f"[LOAD_ESTIMATES] API 네트워크 오류: {e}")
        return JsonResponse({
            'error': 'API 서버 연결 실패',
            'details': str(e)
        }, status=500)

    except Exception as e:
        logger.exception(f"[LOAD_ESTIMATES] 처리 중 서버 오류: {e}")
        return JsonResponse({
            'error': '서버 처리 중 오류 발생',
            'details': str(e)
        }, status=500)


@api_view(['GET'])
@login_required
def received_estimate_detail(request, pk):
    """받은 견적 상세 조회"""
    try:
        # Common API 서버의 실제 엔드포인트로 수정
        response = requests.get(
            f"{settings.COMMON_API_URL}/estimates/estimates/demand/response/{pk}/",
            headers={'Accept': 'application/json'}
        )

        if response.status_code == 200:
            estimate_data = response.json()
            
            # 견적 상태에 따른 한글 표시
            estimate_data['status_display'] = {
                'RESPONSE': '견적서 발송 완료',
                'APPROVED': '승인완료',
                'REJECTED': '거절됨'
            }.get(estimate_data['status'], estimate_data['status'])
            
            return render(request, 'demand/estimates/demand_response_detail.html', {
                'estimate': estimate_data
            })
        else:
            logger.error(f"받은 견적 상세 조회 실패: {response.status_code} - {response.text}")
            return render(request, 'demand/estimates/demand_response_detail.html', {
                'error': '견적 상세 정보를 불러오는데 실패했습니다.'
            })

    except Exception as e:
        logger.error(f"견적 상세 조회 중 오류 발생: {str(e)}")
        return render(request, 'demand/estimates/demand_response_detail.html', {
            'error': '서버와의 통신 중 오류가 발생했습니다.'
        })

@api_view(['GET'])
@login_required
def request_estimate_detail(request, pk):
    """보낸 견적 요청 상세 조회"""
    try:
        response = requests.get(
            f"{settings.COMMON_API_URL}/estimates/estimates/demand/request/{pk}/",
            headers={'Accept': 'application/json'}
        )

        if response.status_code == 200:
            estimate_data = response.json()
            return render(request, 'demand/estimates/demand_request_detail.html', {
                'estimate': estimate_data
            })
        else:
            logger.error(f"견적 요청 상세 조회 실패: {response.status_code} - {response.text}")
            return render(request, 'demand/estimates/demand_request_detail.html', {
                'error': '견적 요청 정보를 불러오는데 실패했습니다.'
            })

    except Exception as e:
        logger.error(f"견적 요청 상세 조회 중 오류 발생: {str(e)}")
        return render(request, 'demand/estimates/demand_request_detail.html', {
            'error': '서버와의 통신 중 오류가 발생했습니다.'
        })

@api_view(['POST'])
@login_required
def estimate_accept(request, pk):
    """견적 수락"""
    try:
        response = requests.post(
            f"{settings.COMMON_API_URL}/estimates/demand/response/{pk}/accept/",
            headers={'Accept': 'application/json'}
        )

        if response.status_code == 200:
            return JsonResponse({'message': '견적이 성공적으로 수락되었습니다.'})
        else:
            return JsonResponse({
                'error': '견적 수락 처리 중 오류가 발생했습니다.'
            }, status=400)

    except Exception as e:
        logger.error(f"견적 수락 처리 중 오류 발생: {str(e)}")
        return JsonResponse({
            'error': '서버와의 통신 중 오류가 발생했습니다.'
        }, status=500)

@api_view(['POST'])
@login_required
def estimate_reject(request, pk):
    """견적 거절"""
    try:
        response = requests.post(
            f"{settings.COMMON_API_URL}/estimates/demand/response/{pk}/reject/",
            headers={'Accept': 'application/json'}
        )

        if response.status_code == 200:
            return JsonResponse({'message': '견적이 성공적으로 거절되었습니다.'})
        else:
            return JsonResponse({
                'error': '견적 거절 처리 중 오류가 발생했습니다.'
            }, status=400)

    except Exception as e:
        logger.error(f"견적 거절 처리 중 오류 발생: {str(e)}")
        return JsonResponse({
            'error': '서버와의 통신 중 오류가 발생했습니다.'
        }, status=500)
