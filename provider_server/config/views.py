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
from users.models import ProviderUser, ProviderEstimate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
import logging
from rest_framework import viewsets, permissions
from rest_framework.decorators import action

ADMIN_PANEL_URL = settings.ADMIN_PANEL_URL
COMMON_API_URL = settings.COMMON_API_URL

logger = logging.getLogger(__name__)

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

# def post(self, request):
#         serializer = ProviderUserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "가입 요청이 접수되었습니다. 관리자의 승인을 기다려주세요."}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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

@api_view(['GET'])
def provider_estimate_list(request): # 필요에 따라 필터 적용
    return render(request, 'provider/estimates/provider_estimate_list.html')


@api_view(['GET'])
def provider_estimate_detail(request):
    return render(request, 'provider/estimates/provider_estimate_detail.html')

@api_view(['GET'])
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


def provider_estimate_accept(request, estimate_id):
    # 수락 처리 로직 추가
    # 예: estimate.status = 'accepted'
    # estimate.save()
    return render(request, 'provider/estimates/provider_estimate_detail.html')


def provider_estimate_form(request):
    return render(request, 'provider/estimates/estimate_form.html')

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

@api_view(['GET'])
@permission_classes([AllowAny])
def received_estimates(request):
    try:
        # 현재 로그인한 사용자의 ID 사용
        provider_user_id = request.user.id
        
        # 쿼리 파라미터 추출
        status = request.GET.get('status')
        search_term = request.GET.get('search', '')

        # 공통 API 서버에서 받은 견적 요청 조회
        common_api_url = f"{settings.COMMON_API_URL}/estimates/estimates/received/"
        
        params = {
            "provider_user_id": provider_user_id,
            "status": status,
            "search": search_term,
            "include_customer_info": True  # 고객 정보 포함 요청
        }

        # 즐겨찾기 탭 처리
        if status == 'FAVORITE':
            params['is_favorited'] = True

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
            return JsonResponse({
                'estimates': [],
                'error': f'API 요청 실패: {response.status_code} - {response.text}'
            }, status=response.status_code)

        estimates_data = response.json()

        # 상태별 개수 계산
        status_counts = {
            'REQUEST': sum(1 for e in estimates_data.get('estimates', []) if e.get('status') == 'REQUEST'),
            'RESPONSE': sum(1 for e in estimates_data.get('estimates', []) if e.get('status') == 'RESPONSE'),
            'APPROVED': sum(1 for e in estimates_data.get('estimates', []) if e.get('status') == 'APPROVED'),
            'REJECTED': sum(1 for e in estimates_data.get('estimates', []) if e.get('status') == 'REJECTED'),
            'FAVORITE': sum(1 for e in estimates_data.get('estimates', []) if e.get('is_favorited'))
        }

        return JsonResponse({
            'estimates': estimates_data.get('estimates', []),
            'total_count': estimates_data.get('total_count', 0),
            'status_counts': status_counts
        }, status=200)
    
    except requests.RequestException as e:
        return JsonResponse({
            'estimates': [],
            'error': f'네트워크 오류: {str(e)}'
        }, status=500)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def estimate_detail(request, pk):
    try:
        # 공통 API 서버에서 견적서 상세 정보 조회
        api_url = f"{settings.COMMON_API_URL}/estimates/estimates/received/{pk}/"
        
        # 디버깅을 위한 로깅 추가
        logger.info(f"📝 견적 상세 조회 API URL: {api_url}")

        response = requests.get(
            api_url, 
            timeout=10,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        # 응답 상태 코드 및 내용 로깅
        logger.info(f"📝 응답 상태 코드: {response.status_code}")
        logger.info(f"📝 응답 내용: {response.text}")

        # 응답 상태 코드 확인
        if response.status_code != 200:
            logger.error(f"⚠️ API 요청 실패: {response.status_code} - {response.text}")
            return JsonResponse({'error': '견적 정보를 불러올 수 없습니다.', 'details': response.text}, status=response.status_code)

        # JSON 데이터 로드
        estimate_data = response.json()
        
        # 고객 정보 추가 조회
        customer_info = None
        if estimate_data.get('demand_user_id'):
            try:
                customer_info_response = requests.get(
                    f"{settings.DEMAND_API_URL}/users/{estimate_data['demand_user_id']}/",
                    timeout=5,
                    headers={'Accept': 'application/json'}
                )
                if customer_info_response.status_code == 200:
                    customer_info = customer_info_response.json()
            except Exception as e:
                logger.error(f"고객 정보 조회 중 오류: {e}")

        # 고객 정보 추가
        estimate_data['customer_info'] = customer_info
        
        # AJAX 요청인지 확인
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(estimate_data)

        # HTML 페이지 렌더링
        return render(request, 'provider/estimates/estimate_detail.html', {
            'estimate_id': pk,
            'estimate_data': estimate_data
        })
    
    except requests.RequestException as e:
        # 네트워크 오류 처리
        logger.error(f"🚨 견적서 조회 중 네트워크 오류: {e}")
        return JsonResponse({
            'error': '견적서 조회 중 네트워크 오류가 발생했습니다.',
            'details': str(e)
        }, status=500)
    

@api_view(['GET'])
def check_estimate_exists(request, pk):
    """견적 존재 여부 확인"""
    try:
        logger.info(f"견적 존재 여부 확인 - 견적 요청 ID: {pk}")
        
        # 해당 견적 요청에 대한 provider의 견적서 조회
        existing_estimate = ProviderEstimate.objects.filter(
            estimate_request_id=pk,
            provider=request.user 
        ).first()

        logger.info(f"조회된 견적: {existing_estimate}")

        if existing_estimate:
            return JsonResponse({
                'exists': True,
                'estimate_id': existing_estimate.id,
                'status': existing_estimate.status
            })
        else:
            return JsonResponse({
                'exists': False
            })

    except Exception as e:
        logger.error(f"견적 존재 여부 확인 중 오류: {e}")
        return JsonResponse({
            'error': str(e)
        }, status=500)

@api_view(['GET', 'POST'])
def provider_estimate_form(request, pk):
    """견적서 조회 및 저장"""
    try:
        if request.method == 'GET':
            # 견적 요청 정보 조회
            response = requests.get(
                f"{settings.COMMON_API_URL}/estimates/estimates/received/{pk}/",
                headers={'Accept': 'application/json'}
            )
            response.raise_for_status()
            estimate_data = response.json()
            
            logger.info(f"받은 견적 요청 데이터: {estimate_data}")

            # 고객 정보 조회
            customer_info = None
            if estimate_data.get('demand_user_id'):
                try:
                    customer_info_response = requests.get(
                        f"{settings.DEMAND_API_URL}/users/{estimate_data['demand_user_id']}/",
                        timeout=5,
                        headers={'Accept': 'application/json'}
                    )
                    if customer_info_response.status_code == 200:
                        customer_info = customer_info_response.json()
                except Exception as e:
                    logger.error(f"고객 정보 조회 중 오류: {e}")

            # 기존 견적서 조회
            existing_estimate = ProviderEstimate.objects.filter(
                estimate_request_id=pk,
                provider=request.user
            ).first()

            context = {
                'original_request': estimate_data,
                'customer': customer_info,
                'estimate_id': pk,
                'existing_estimate': existing_estimate
            }
            
            return render(request, 'provider/estimates/estimate_form.html', context)

        elif request.method == 'POST':
            logger.info(f"견적서 저장 요청 - 견적 요청 ID: {pk}")
            
            # 요청 데이터 파싱
            measurement_items = json.loads(request.POST.get('measurement_items', '[]'))
            total_amount = request.POST.get('total_amount', '0').replace(',', '')  # 콤마 제거
            status = request.POST.get('status', 'DRAFT')
            notes = request.POST.get('notes', '')

            logger.info(f"측정 항목: {measurement_items}")
            logger.info(f"총 금액: {total_amount}")

            # 견적서 생성 또는 업데이트
            estimate, created = ProviderEstimate.objects.update_or_create(
                estimate_request_id=pk,
                provider=request.user,
                defaults={
                    'maintain_points': sum(item.get('maintain_points', 0) for item in measurement_items),
                    'recommend_points': sum(item.get('recommend_points', 0) for item in measurement_items),
                    'unit_price': measurement_items[0].get('unit_price', 0) if measurement_items else 0,
                    'total_amount': total_amount,
                    'status': status,
                    'notes': notes
                }
            )

            # 공통 API 서버에 상태 업데이트
            common_api_data = {
                'status': 'RESPONSE',
                'provider_user_id': request.user.id,
                'measurement_items': measurement_items,
                'total_amount': total_amount,
                'notes': notes
            }

            response = requests.put(
                f"{settings.COMMON_API_URL}/estimates/estimates/{pk}/",
                json=common_api_data,
                headers={'Accept': 'application/json'}
            )
            response.raise_for_status()

            # 📌 파일 업로드 처리
        for file_key, file in request.FILES.items():
            EstimateFile.objects.create(estimate=estimate, file_type=file_key, file=file)


            return JsonResponse({
                'success': True,
                'message': '견적이 저장되었습니다.',
                'estimate_id': estimate.id,
                'redirect_url': f'/estimate_list/estimates/received/{estimate.id}/view/'
            })

    except requests.RequestException as e:
        logger.error(f"API 요청 중 오류: {e}")
        return JsonResponse({
            'error': 'API 서버 통신 중 오류가 발생했습니다.',
            'details': str(e)
        }, status=500)
    except Exception as e:
        logger.error(f"견적 처리 중 오류: {e}")
        return JsonResponse({
            'error': '견적 처리 중 오류가 발생했습니다.',
            'details': str(e)
        }, status=500)

@api_view(['GET'])
def provider_estimate_form_view(request, pk):
    """견적 조회 또는 작성 페이지로 이동"""
    try:
        logger.info(f"견적 조회/작성 페이지 요청 - 견적 요청 ID: {pk}")
        
        # 견적 존재 여부 확인
        existing_estimate = ProviderEstimate.objects.filter(
            estimate_request_id=pk,
            provider=request.user 
        ).first()

        if existing_estimate:
            # 기존 견적서가 있는 경우 조회 페이지로
            context = {
                'estimate': existing_estimate,
                'can_edit': existing_estimate.status in ['DRAFT', 'SAVED'],
                'can_send': existing_estimate.status in ['DRAFT', 'SAVED']
            }
            return render(request, 'provider/estimates/estimate_form_view.html', context)
        else:
            # 기존 견적서가 없는 경우 작성 페이지로
            return render(request, 'provider/estimates/estimate_form.html', {
                'estimate_request_id': pk
            })

    except Exception as e:
        logger.error(f"견적 조회/작성 페이지 이동 중 오류: {e}")
        return JsonResponse({
            'error': '견적 조회 중 오류가 발생했습니다.',
            'details': str(e)
        }, status=500)
    

@api_view(['PUT'])
def provider_estimate_form_update(request, pk):
    """견적 수정"""
    try:
        # 견적서 조회
        provider_estimate = ProviderEstimate.objects.filter(
            estimate_request_id=pk,
            provider=request.user
        ).first()
        
        if not provider_estimate:
            return JsonResponse({
                'error': '해당 견적서를 찾을 수 없습니다.'
            }, status=404)
        
        # 수정 가능한 상태인지 확인
        if provider_estimate.status not in ['DRAFT', 'SAVED']:
            return JsonResponse({
                'error': '수정할 수 없는 상태의 견적서입니다.'
            }, status=400)

        # 데이터 업데이트
        estimate_data = request.data
        for field, value in estimate_data.items():
            if hasattr(provider_estimate, field):
                setattr(provider_estimate, field, value)
        
        provider_estimate.save()
        
        return JsonResponse({
            'success': True,
            'message': '견적이 수정되었습니다.',
            'estimate_id': provider_estimate.id,
            'redirect_url': f'/estimate_list/estimates/received/{provider_estimate.id}/view/'
        })

    except Exception as e:
        logger.error(f"견적 수정 중 오류 발생: {e}")
        return JsonResponse({
            'error': str(e)
        }, status=500)
    

@api_view(['POST'])
def provider_send_estimate(request, pk):
    """견적 발송"""
    try:
        response = requests.post(
            f"{settings.COMMON_API_URL}/estimates/estimates/{pk}/send/",
            headers={'Accept': 'application/json'}
        )
        response.raise_for_status()
        
        # 견적 발송 알림 전송
        notification_data = {
            'estimate_id': pk,
            'type': 'ESTIMATE_SENT',
            'message': '견적서가 발송되었습니다.'
        }
        
        requests.post(
            f"{settings.COMMON_API_URL}/notifications/",
            json=notification_data,
            headers={'Accept': 'application/json'}
        )
        
        return JsonResponse({'message': '견적이 발송되었습니다.'})

    except Exception as e:
        logger.error(f"견적 발송 중 오류 발생: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@permission_classes([AllowAny])
class ReceivedEstimateViewSet(viewsets.ViewSet):
    authentication_classes = []  # ✅ 인증 비활성화
    permission_classes = [AllowAny]  # ✅ 누구나 접근 가능

    def list(self, request):
        """받은 견적 목록 조회"""
        try:
            # 현재 로그인한 Provider의 ID 사용
            provider_user_id = request.user.id
            
            # 쿼리 파라미터 추출
            params = {
                'provider_user_id': provider_user_id,
                'status': request.query_params.get('status', ''),
                'search': request.query_params.get('search', ''),
                'include_customer_info': True,
                'page': request.query_params.get('page', 1),
                'page_size': request.query_params.get('page_size', 10)
            }

            # 로깅
            logger.info(f"받은 견적 목록 조회 - Provider ID: {provider_user_id}")
            logger.info(f"필터 파라미터: {params}")

            # 공통 API 서버에서 견적 데이터 요청
            response = requests.get(
                f"{settings.COMMON_API_URL}/estimates/estimates/received/", 
                params=params,
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )

            # 응답 로깅
            logger.info(f"공통 API 서버 응답 상태: {response.status_code}")

            # 응답 처리
            if response.status_code == 200:
                estimates_data = response.json()
                return Response({
                    'estimates': estimates_data.get('estimates', []),
                    'total_count': estimates_data.get('total_count', 0),
                    'status_counts': estimates_data.get('status_counts', {}),
                    'pagination': {
                        'current_page': estimates_data.get('page', 1),
                        'total_pages': estimates_data.get('total_pages', 1),
                        'page_size': estimates_data.get('page_size', 10)
                    }
                })
            else:
                logger.error(f"API 요청 실패: {response.status_code} - {response.text}")
                return Response(
                    {
                        'estimates': [],
                        'error': f'API 요청 실패: {response.status_code}',
                        'detail': response.text
                    }, 
                    status=response.status_code
                )

        except requests.RequestException as e:
            logger.error(f"네트워크 오류: {e}")
            return Response(
                {
                    'estimates': [],
                    'error': '네트워크 오류 발생',
                    'detail': str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """특정 견적 상세 조회"""
        try:
            # 현재 로그인한 Provider의 ID 사용
            provider_user_id = request.user.id
            
            # 공통 API 서버에서 견적 상세 정보 요청
            response = requests.get(
                f"{settings.COMMON_API_URL}/estimates/estimates/received/{pk}/", 
                # params={'provider_user_id': provider_user_id},
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )

            # 로깅
            logger.info(f"받은 견적 상세 조회 - Provider ID: {provider_user_id}, 견적 ID: {pk}")
            logger.info(f"공통 API 서버 응답 상태: {response.status_code}")

            # 응답 처리
            if response.status_code == 200:
                estimate_data = response.json()
                
                # 고객 정보 추가 조회
                if estimate_data.get('demand_user_id'):
                    try:
                        customer_info_response = requests.get(
                            f"{settings.DEMAND_API_URL}/users/{estimate_data['demand_user_id']}/",
                            timeout=5,
                            headers={'Accept': 'application/json'}
                        )
                        if customer_info_response.status_code == 200:
                            estimate_data['customer_info'] = customer_info_response.json()
                    except Exception as e:
                        logger.error(f"고객 정보 조회 중 오류: {e}")
                        estimate_data['customer_info'] = None

                return Response(estimate_data)
            elif response.status_code == 404:
                return Response(
                    {'error': '해당 견적을 찾을 수 없습니다.'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            else:
                logger.error(f"API 요청 실패: {response.status_code} - {response.text}")
                return Response(
                    {
                        'error': '견적 상세 정보를 불러오는 중 오류가 발생했습니다.',
                        'detail': response.text
                    }, 
                    status=response.status_code
                )

        except requests.RequestException as e:
            logger.error(f"네트워크 오류: {e}")
            return Response(
                {
                    'error': '네트워크 오류 발생',
                    'detail': str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['POST'])
    def respond(self, request, pk=None):
        """견적에 대한 응답 처리"""
        try:
            # 응답 데이터 검증
            response_data = request.data
            
            # 공통 API 서버로 응답 전달
            response = requests.post(
                f"{settings.COMMON_API_URL}/estimates/received/{pk}/respond/",
                json=response_data,
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )

            # 응답 처리
            if response.status_code == 200:
                return Response(response.json())
            else:
                logger.error(f"응답 처리 실패: {response.status_code} - {response.text}")
                return Response(
                    {
                        'error': '견적 응답 처리 중 오류가 발생했습니다.',
                        'detail': response.text
                    },
                    status=response.status_code
                )

        except requests.RequestException as e:
            logger.error(f"네트워크 오류: {e}")
            return Response(
                {
                    'error': '네트워크 오류 발생',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_star_estimate(request):
    """견적 즐겨찾기 토글"""
    try:
        estimate_id = request.data.get('estimate_id')
        
        if not estimate_id:
            return Response(
                {"error": "견적 ID가 필요합니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 견적 조회
        estimate = get_object_or_404(Estimate, id=estimate_id)
        
        # 즐겨찾기 토글
        is_favorited = estimate.toggle_favorite(request.user)

        return Response({
            "success": True,
            "estimate_id": estimate.id,
            "is_favorited": is_favorited
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"즐겨찾기 토글 중 오류: {str(e)}")
        return Response({
            "error": "즐겨찾기 토글 중 오류가 발생했습니다.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

