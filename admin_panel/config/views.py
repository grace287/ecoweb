from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from users.models import Company, AdminUser, DemandUser, ProviderUser  # DemandUser와 ProviderUser 추가
from django.db.models import Q, Count
import requests
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.core.exceptions import ValidationError
from .fake_data import create_fake_data
import json
from django.views.decorators.csrf import csrf_exempt

import logging

logger = logging.getLogger(__name__)


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

def fetch_provider_signup_requests():
    """Provider 서버에서 가입 대기 중인 유저 목록 가져오기"""
    try:
        # 여러 가능한 엔드포인트 시도
        endpoints = [
            f"{settings.PROVIDER_API_URL}/signup/pending/",
            f"{settings.PROVIDER_API_URL}/provider_pending_list/",
            f"{settings.PROVIDER_API_URL}/api/provider_pending_list/",
        ]

        for url in endpoints:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                logger.info(f"엔드포인트 {url} 요청 상태: {response.status_code}")

                # 응답 상태 코드 확인
                if response.status_code != 200:
                    logger.warning(f"❌ {url} 서버 요청 실패: {response.status_code} - {response.text}")
                    continue

                # 응답이 비어 있는 경우 예외 처리
                raw_data = response.text.strip()
                if not raw_data:
                    logger.warning(f"⚠️ {url} 서버 응답이 비어 있습니다.")
                    continue

                # HTML 응답인지 확인
                if "<html" in raw_data.lower():
                    logger.error(f"❌ {url} 예상치 못한 HTML 응답: {raw_data[:500]}")
                    continue

                # JSON 응답 검증
                try:
                    signup_requests = json.loads(raw_data)
                    
                    # JSON이 리스트인지 확인 (아닐 경우 딕셔너리에서 'requests' 키 찾기)
                    if not isinstance(signup_requests, list):
                        if isinstance(signup_requests, dict):
                            signup_requests = signup_requests.get('requests', [])
                            signup_requests = signup_requests or signup_requests.get('pending_users', [])
                        else:
                            logger.error(f"❌ 예상치 못한 응답 형식: {signup_requests}")
                            continue
                    
                    # 데이터 표준화
                    for request_item in signup_requests:
                        request_item['id'] = request_item.get('id') or request_item.get('username', 'unknown')
                        request_item['company_name'] = request_item.get('company_name', '미입력')
                        request_item['username'] = request_item.get('username', 'unknown')
                        request_item['email'] = request_item.get('email', '')
                        request_item['business_registration_number'] = request_item.get('business_registration_number', '')
                        request_item['business_phone_number'] = request_item.get('business_phone_number', '')
                        request_item['is_approved'] = request_item.get('is_approved', False)
                        request_item['created_at'] = request_item.get('created_at') or timezone.now().isoformat()

                    logger.info(f"✅ {url} 서버 가입 요청 목록: {signup_requests}")
                    return signup_requests

                except json.JSONDecodeError:
                    logger.error(f"❌ {url} 서버 응답이 JSON 형식이 아님: {raw_data[:500]}")
                    continue

            except requests.RequestException as e:
                logger.error(f"❌ {url} 서버 API 요청 중 오류 발생: {e}")
                continue

        # 모든 엔드포인트 시도 후 실패한 경우
        logger.error("모든 엔드포인트에서 가입 요청 목록을 불러오는 데 실패했습니다.")
        
        # 로컬 데이터베이스에서 대기 중인 사용자 가져오기
        local_pending_users = ProviderUser.objects.filter(is_approved=False).values(
            'username', 
            'company_name', 
            'email', 
            'business_registration_number', 
            'business_phone_number',
            'created_at'
        )
        
        # 로컬 데이터 표준화
        local_pending_list = list(local_pending_users)
        for user in local_pending_list:
            user['id'] = user.get('username')
            user['is_approved'] = False
        
        logger.info(f"로컬 데이터베이스에서 {len(local_pending_list)}개의 대기 중인 사용자를 찾았습니다.")
        return local_pending_list

    except Exception as e:
        logger.error(f"가입 요청 목록 불러오기 중 예상치 못한 오류 발생: {e}")
        return []



@csrf_exempt
def sync_provider_signup(request):
    """Provider 서버로부터 가입 요청 동기화"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # 이미 존재하는 경우 업데이트, 없으면 생성
            provider_user, created = ProviderUser.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'company_name': data['company_name'],
                    'business_registration_number': data['business_registration_number'],
                    'business_phone_number': data['business_phone_number'],
                    'is_approved': False,
                    'is_active': False
                }
            )
            
            return JsonResponse({
                "success": True, 
                "message": "동기화 완료",
                "created": created
            })
        
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

@login_required
def approve_provider_requests(request):
    """대행사 가입 요청 승인/거부"""

    try:
        pending_requests = fetch_provider_signup_requests()
        logger.info(f"불러온 가입 요청 목록: {pending_requests}")
    except Exception as e:
        logger.error(f"가입 요청 목록 불러오기 실패: {e}")
        pending_requests = []

    # 로컬 데이터베이스에서 대기 중인 사용자 추가
    if not pending_requests:
        local_pending_users = ProviderUser.objects.filter(is_approved=False).values(
            'username', 
            'company_name', 
            'email', 
            'business_registration_number', 
            'business_phone_number',
            'created_at'
        )
        pending_requests = list(local_pending_users)
        for user in pending_requests:
            user['id'] = user.get('username')
            user['is_approved'] = False

    if request.method == "POST":
        # 요청 본문 전체 로깅
        logger.info(f"전체 요청 메타데이터: {request.META}")
        logger.info(f"요청 본문 (raw): {request.body}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"요청 인코딩: {request.encoding}")

        # 요청 데이터 파싱
        try:
            # 요청 본문이 비어있는지 확인
            if not request.body:
                logger.error("요청 본문이 비어있습니다.")
                return JsonResponse({
                    "success": False, 
                    "error": "요청 본문이 비어있습니다."
                }, status=400)

            # JSON 본문 직접 디코딩
            raw_body = request.body.decode('utf-8', errors='ignore').strip()
            logger.info(f"디코딩된 본문: {raw_body}")
            
            # 빈 문자열 확인
            if not raw_body:
                logger.error("디코딩된 본문이 비어있습니다.")
                return JsonResponse({
                    "success": False, 
                    "error": "유효한 JSON 데이터가 없습니다."
                }, status=400)

            try:
                data = json.loads(raw_body)
            except json.JSONDecodeError as e:
                logger.error(f"JSON 디코딩 오류: {e}")
                return JsonResponse({
                    "success": False, 
                    "error": f"JSON 디코딩 오류: {str(e)}"
                }, status=400)

        except Exception as e:
            logger.error(f"요청 데이터 처리 중 예외 발생: {e}")
            return JsonResponse({
                "success": False, 
                "error": f"요청 데이터 처리 중 오류: {str(e)}"
            }, status=400)

        # 로깅된 데이터 출력
        logger.info(f"파싱된 데이터: {data}")

        # 필수 파라미터 검증
        user_id = data.get("user_id")
        action = data.get("action")

        # 추가 로깅
        logger.info(f"user_id 타입: {type(user_id)}, 값: {user_id}")
        logger.info(f"action 타입: {type(action)}, 값: {action}")

        if not user_id or action not in ["approve", "reject"]:
            logger.error(f"유효하지 않은 요청 데이터: user_id={user_id}, action={action}")
            return JsonResponse({
                "success": False, 
                "error": "유효한 요청 데이터가 필요합니다."
            }, status=400)

        # 선택적 파라미터
        reason = data.get("reason", "")

        try:
            # user_id를 문자열로 변환하여 검색
            provider_user = ProviderUser.objects.get(username=str(user_id))
        except ProviderUser.DoesNotExist:
            return JsonResponse({
                "success": False, 
                "error": "해당 사용자를 찾을 수 없습니다."
            }, status=404)

        # ✅ Provider 서버 승인/거부 요청 전송
        api_url = f"{settings.PROVIDER_API_URL}/update_user_status/"
        api_data = {
            "username": provider_user.username,
            "is_approved": action == "approve",
            "reason": reason if action == "reject" else ""
        }

        try:
            response = requests.post(api_url, json=api_data, headers={"Content-Type": "application/json"}, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Provider 서버 업데이트 실패: {e}")
            return JsonResponse({
                "success": False, 
                "error": "Provider 서버 업데이트 실패"
            }, status=500)

        # ✅ 로컬 데이터베이스 업데이트
        if action == "approve":
            provider_user.is_approved = True
            provider_user.is_active = True
            provider_user.approved_at = timezone.now()
            provider_user.save()
            message = f"{provider_user.company_name} 업체가 승인되었습니다."

            Company.objects.get_or_create(
                provider_user=provider_user,
                defaults={
                    'username': provider_user.username,
                    'email': provider_user.email,
                    'company_name': provider_user.company_name,
                    'business_registration_number': provider_user.business_registration_number,
                    'business_phone_number': provider_user.business_phone_number,
                    'user_type': 'provider',
                    'status': 'approved',
                    'approved_by': request.user,
                    'approved_at': timezone.now()
                }
            )
        else:
            provider_user.is_approved = False
            provider_user.is_active = False
            provider_user.rejection_reason = reason
            provider_user.save()
            message = f"{provider_user.company_name} 업체가 거부되었습니다."

        return JsonResponse({
            "success": True, 
            "message": message
        })

    # ✅ AJAX 요청이면 JSON 반환
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"pending_requests": pending_requests}, status=200)

    return render(request, "admin_panel/approve_requests.html", {"pending_requests": pending_requests})



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
    """업체 리스트 페이지 - 모든 가입 요청 포함"""
    try:
        # Provider 서버에서 모든 가입 요청 목록 가져오기
        response = requests.get(
            f"{settings.PROVIDER_API_URL}/signup/all/", 
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # API 호출 성공 시
        if response.status_code == 200:
            # 로깅을 통해 실제 응답 확인
            logger.info(f"Provider 서버 전체 가입 요청 응답: {response.text}")
            
            try:
                # 다양한 응답 형식에 대응
                raw_data = response.text.strip()
                if not raw_data:
                    logger.error("빈 응답")
                    all_provider_requests = []
                elif raw_data.startswith('{'):
                    # JSON 객체인 경우
                    data = json.loads(raw_data)
                    all_provider_requests = data.get('requests', []) if isinstance(data, dict) else []
                elif raw_data.startswith('['):
                    # JSON 배열인 경우
                    all_provider_requests = json.loads(raw_data)
                else:
                    logger.error(f"알 수 없는 응답 형식: {raw_data}")
                    all_provider_requests = []
            except json.JSONDecodeError:
                logger.error(f"JSON 디코딩 오류: {raw_data}")
                all_provider_requests = []
            
            # 데이터 표준화
            for request_item in all_provider_requests:
                request_item['id'] = request_item.get('id') or request_item.get('username', 'unknown')
                request_item['company_name'] = request_item.get('company_name', '미입력')
                request_item['username'] = request_item.get('username', 'unknown')
                request_item['email'] = request_item.get('email', '')
                request_item['business_registration_number'] = request_item.get('business_registration_number', '')
                request_item['business_phone_number'] = request_item.get('business_phone_number', '')
                request_item['is_approved'] = request_item.get('is_approved', False)
                request_item['created_at'] = request_item.get('created_at') or timezone.now().isoformat()
        else:
            logger.error(f"Provider 서버 요청 실패: {response.status_code}")
            all_provider_requests = []

        # 로컬 데이터베이스의 기존 데이터와 병합
        local_demand_users = DemandUser.objects.all()
        local_provider_users = ProviderUser.objects.all()
        local_companies = Company.objects.all().order_by('-created_at')

        context = {
            "demand_users": local_demand_users,
            "provider_users": local_provider_users,
            "companies": local_companies,
            "provider_requests": all_provider_requests
        }

        return render(request, 'dashboard/company_list.html', context)
    
    except Exception as e:
        # 모든 예외 처리
        logger.error(f"업체 목록 처리 중 오류 발생: {e}")
        messages.error(request, "업체 목록을 불러오는 중 오류가 발생했습니다.")
        
        # 로컬 데이터만 반환
        context = {
            "demand_users": DemandUser.objects.all(),
            "provider_users": ProviderUser.objects.all(),
            "companies": Company.objects.all().order_by('-created_at'),
            "provider_requests": []
        }
        return render(request, 'dashboard/company_list.html', context)

@login_required
def company_detail(request, pk):
    try:
        # ProviderUser 모델로 변경
        provider_user = ProviderUser.objects.get(pk=pk)
        return render(request, 'dashboard/company_detail.html', {'company': provider_user})
    except ProviderUser.DoesNotExist:
        messages.error(request, '해당 업체를 찾을 수 없습니다.')
        return redirect('approve_provider_requests')

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



def provider_users_view(request):
    """Django 뷰에서 Provider 서버의 유저 데이터를 JSON으로 반환"""
    provider_users = fetch_provider_users()
    return JsonResponse({"provider_users": provider_users})

def generate_fake_data_view(request):
    """가짜 데이터 생성 뷰"""
    create_fake_data()
    return JsonResponse({
        "status": "success", 
        "message": "가짜 데이터가 성공적으로 생성되었습니다."
    })