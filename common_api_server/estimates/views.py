import requests
from django.conf import settings
from django.http import JsonResponse
import json
from services.models import ServiceCategory
from .models import Estimate, MeasurementLocation
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import (
    EstimateListSerializer, 
    EstimateDetailSerializer, 
    EstimateCreateSerializer,
    EstimateSerializer,
    ReceivedEstimateSerializer
)
from rest_framework import status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
from rest_framework import viewsets, permissions
from rest_framework.decorators import action

logger = logging.getLogger(__name__)

def get_demand_user_info(user_id):
    """Demand 서버에서 사용자 정보 가져오기"""
    url = f"{settings.DEMAND_API_URL}/users/{user_id}/"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def get_provider_user_info(provider_id):
    """Provider 서버에서 사용자 정보 가져오기"""
    url = f"{settings.PROVIDER_API_URL}/users/{provider_id}/"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None


@csrf_exempt
def create_estimate(request):
    """견적서 생성 API"""
    try:
        data = json.loads(request.body)
        
        # 필수 필드 검증
        required_fields = ['service_category_codes', 'measurement_location_id', 'address', 'preferred_schedule']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({"error": f"{field}는 필수 항목입니다."}, status=400)

        # 서비스 카테고리 검증 (다중 카테고리)
        try:
            categories = ServiceCategory.objects.filter(category_code__in=data['service_category_codes'])
            if len(categories) != len(data['service_category_codes']):
                return JsonResponse({"error": "유효하지 않은 서비스 카테고리가 포함되어 있습니다."}, status=400)
        except ServiceCategory.DoesNotExist:
            return JsonResponse({"error": "유효하지 않은 서비스 카테고리입니다."}, status=400)

        # 측정 장소 검증
        try:
            location = MeasurementLocation.objects.get(id=data['measurement_location_id'])
        except MeasurementLocation.DoesNotExist:
            return JsonResponse({"error": "유효하지 않은 측정 장소입니다."}, status=400)

        # 담당자 정보 처리
        contact_info = {
            'contact_name': '미지정',
            'contact_phone': '',
            'contact_email': '',
            'demand_user_id': None
        }

        # 로그인된 사용자의 경우 기본 정보 추가
        if request.user.is_authenticated:
            contact_info.update({
                'demand_user_id': request.user.id,
                'contact_name': request.user.name if hasattr(request.user, 'name') else request.user.username,
                'contact_email': request.user.email
            })

        # 사용자가 직접 입력한 담당자 정보가 있다면 우선 적용
        if data.get('contact_info'):
            contact_info.update({
                'contact_name': data['contact_info'].get('name', contact_info['contact_name']),
                'contact_phone': data['contact_info'].get('phone', contact_info['contact_phone']),
                'contact_email': data['contact_info'].get('email', contact_info['contact_email'])
            })

        # 견적서 생성
        # 첫 번째 카테고리를 기본 카테고리로 설정
        primary_category = categories.first()
        
        estimate = Estimate.objects.create(
            service_category=primary_category,  # 첫 번째 카테고리를 기본으로 설정
            address=data['address'],
            preferred_schedule=data.get('preferred_schedule', 'asap'),
            status='REQUEST',
            demand_user_id=contact_info['demand_user_id'],
            contact_name=contact_info['contact_name'],
            contact_phone=contact_info['contact_phone'],
            contact_email=contact_info['contact_email'],
            provider_user_id=data.get('provider_user_id')
        )
        
        # 다중 카테고리 연결
        estimate.service_categories.set(categories)
        estimate.measurement_locations.add(location)

        # 새로 추가: Provider 서버로 견적 전달
        provider_response = forward_estimate_to_provider(estimate)

        # Provider 서버 전달 결과에 따른 처리
        if provider_response is None:
            # Provider 서버 전달 실패 시 로깅
            print(f"⚠️ 견적 {estimate.id}의 Provider 서버 전달 실패")
            # 필요하다면 estimate의 상태를 업데이트하거나 추가 처리 가능


        return JsonResponse({
            "success": True,
            "estimate_id": estimate.id,
            "estimate_number": estimate.estimate_number,
            "message": "견적 요청이 성공적으로 생성되었습니다.",
            "contact_info": {
                "name": contact_info['contact_name'],
                "phone": contact_info['contact_phone'],
                "email": contact_info['contact_email']
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def forward_estimate_to_provider(estimate):
    """공통 API 서버에서 Provider 서버로 견적 요청을 전달하는 함수"""
    try:
        PROVIDER_API_URL = settings.PROVIDER_API_URL  # settings에서 URL 가져오기
        provider_url = f"{PROVIDER_API_URL}/estimates/"
        
        payload = {
            "estimate_id": estimate.id,
            "service_category_codes": [cat.category_code for cat in estimate.service_categories.all()],
            "measurement_location_id": estimate.measurement_locations.first().id if estimate.measurement_locations.exists() else None,
            "address": estimate.address,
            "preferred_schedule": estimate.preferred_schedule,
            "status": estimate.status,
            "contact_info": {
                "name": estimate.contact_name,
                "phone": estimate.contact_phone,
                "email": estimate.contact_email
            }
        }

        # 로깅 추가
        print(f"📤 Provider 서버로 견적 전달: {payload}")

        response = requests.post(
            provider_url, 
            json=payload,
            timeout=5,  # 타임아웃 설정
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )

        # 응답 로깅
        print(f"📥 Provider 서버 응답 상태: {response.status_code}")
        print(f"📥 Provider 서버 응답 내용: {response.text}")

        if response.status_code not in [200, 201]:
            print(f"⚠️ Provider 서버에 견적 전달 실패: {response.status_code}, {response.text}")
            return None
        
        return response.json()

    except requests.RequestException as e:
        # 네트워크 오류 처리
        print(f"🚨 Provider 서버 통신 중 오류 발생: {e}")
        return None
    except Exception as e:
        # 예상치 못한 오류 처리
        print(f"🚨 예상치 못한 오류: {e}")
        return None
    
def filter_estimates(queryset, provider_user_id=None, demand_user_id=None, status_filter=None, search_term=None):
    """
    견적 쿼리셋에 대한 공통 필터링 메서드
    
    :param queryset: 기본 쿼리셋
    :param provider_user_id: Provider 사용자 ID
    :param demand_user_id: Demand 사용자 ID
    :param status_filter: 상태 필터
    :param search_term: 검색어
    :return: 필터링된 쿼리셋
    """
    if provider_user_id:
        queryset = queryset.filter(provider_user_id=provider_user_id)
    
    if demand_user_id:
        queryset = queryset.filter(demand_user_id=demand_user_id)
    
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    if search_term:
        queryset = queryset.filter(
            Q(service_category__name__icontains=search_term) | 
            Q(address__icontains=search_term)
        )
    
    return queryset

def prepare_estimate_response(estimates):
    """
    견적 데이터를 표준화된 형식으로 변환
    
    :param estimates: Estimate 쿼리셋
    :return: 직렬화된 견적 데이터 리스트
    """
    return [
        {
            "id": e.id,
            "estimate_number": e.estimate_number,
            "service_category": e.service_category.name if e.service_category else "미지정",
            "status": e.status,
            "address": e.address,
            "preferred_schedule": e.get_preferred_schedule_display(),
            "created_at": e.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "contact_name": e.contact_name,
            "contact_phone": e.contact_phone,
            "contact_email": e.contact_email,
            "measurement_locations": [
                loc.name for loc in e.measurement_locations.all()
            ],
            "service_categories": [
                cat.name for cat in e.service_categories.all()
            ]
        }
        for e in estimates
    ]

@login_required
def get_estimate_list(request):
    """견적 리스트 조회 API"""
    # 파라미터 추출
    provider_user_id = request.GET.get("provider_user_id")
    demand_user_id = request.GET.get("demand_user_id")
    status = request.GET.get("status", "")
    search_term = request.GET.get("search", "")

    # 로깅
    logger.info(f"견적 리스트 조회 파라미터: provider_user_id={provider_user_id}, status={status}, search_term={search_term}")

    # 견적 필터링
    estimates = filter_estimates(
        Estimate.objects.all(), 
        provider_user_id=provider_user_id, 
        demand_user_id=demand_user_id, 
        status_filter=status, 
        search_term=search_term
    )

    # 응답 준비
    result = prepare_estimate_response(estimates)

    return JsonResponse({"estimates": result, "total_count": estimates.count()}, status=200)


# 서비스 카테고리 목록 API 추가
@csrf_exempt
def get_service_categories(request):
    """서비스 카테고리 목록 조회 API"""
    if request.method != "GET":
        return JsonResponse({"error": "잘못된 요청 방식입니다."}, status=405)
        
    categories = ServiceCategory.objects.all()
    data = [{
        'code': category.category_code,
        'name': category.name,
        'description': category.description,
        'measurement_items': category.get_measurement_items(),  # 측정 항목 추가
    } for category in categories]
    
    return JsonResponse({"categories": data})

def estimate_request_view(request):
    context = {
        'user': request.user,
        # 기타 필요한 컨텍스트 변수들
    }
    return render(request, 'demand/estimates/estimate_request_form.html', context)


@csrf_exempt
def get_measurement_locations(request):
    """✅ 측정 장소 목록 조회 API"""
    try:
        locations = MeasurementLocation.objects.all()
        if not locations.exists():
            return JsonResponse({"locations": [], "message": "등록된 측정 장소가 없습니다."}, status=200)

        data = [{
            'id': location.id,
            'name': location.name
        } for location in locations]

        return JsonResponse({"locations": data}, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        return JsonResponse({"error": f"측정 장소 조회 실패: {str(e)}"}, status=500)

def estimate_detail(request, estimate_id):
    """견적서 상세 정보 조회"""
    try:
        # 특정 견적서 조회 (존재하지 않으면 404 에러)
        estimate = get_object_or_404(Estimate, id=estimate_id)
        
        # 견적서 상세 정보 컨텍스트 생성
        context = {
            'estimate': {
                'id': estimate.id,
                'estimate_number': estimate.estimate_number,
                'service_category': estimate.service_category.name if estimate.service_category else '미지정',
                'address': estimate.address,
                'preferred_schedule': estimate.get_preferred_schedule_display(),
                'status': estimate.get_status_display(),
                'created_at': estimate.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'measurement_locations': [loc.name for loc in estimate.measurement_locations.all()]
            }
        }
        
        return render(request, 'estimates/estimate_detail.html', context)
    
    except Exception as e:
        # 예상치 못한 오류 처리
        return JsonResponse({
            'error': '견적서 조회 중 오류가 발생했습니다.',
            'details': str(e)
        }, status=500)

@csrf_exempt
def update_estimate(request, estimate_id):
    """Provider 서버가 견적서 업데이트 (응답)"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            estimate = Estimate.objects.get(id=estimate_id)

            estimate.provider_user_id = data.get("provider_user_id")
            estimate.base_amount = data.get("base_amount", estimate.base_amount)
            estimate.discount_amount = data.get("discount_amount", estimate.discount_amount)
            estimate.status = "RESPONSE"  # 견적 응답 처리

            estimate.save()
            return JsonResponse({"success": True, "message": "견적이 업데이트되었습니다."}, status=200)

        except Estimate.DoesNotExist:
            return JsonResponse({"error": "존재하지 않는 견적입니다."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)

    return JsonResponse({"error": "잘못된 요청 방식입니다."}, status=405)

class EstimateViewSet(viewsets.ModelViewSet):
    queryset = Estimate.objects.all()
    serializer_class = EstimateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        선택적 필터링을 위한 쿼리셋 커스터마이징
        """
        queryset = super().get_queryset()
        provider_user_id = self.request.query_params.get('provider_user_id')
        demand_user_id = self.request.query_params.get('demand_user_id')
        status_filter = self.request.query_params.get('status')
        search_term = self.request.query_params.get('search')

        if provider_user_id:
            queryset = queryset.filter(provider_user_id=provider_user_id)
        
        if demand_user_id:
            queryset = queryset.filter(demand_user_id=demand_user_id)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if search_term:
            queryset = queryset.filter(
                Q(service_category__name__icontains=search_term) | 
                Q(address__icontains=search_term)
            )
        
        return queryset

    @action(detail=False, methods=['GET'], url_path='received')
    def received_estimates(self, request):
        """
        받은 견적 요청 목록 조회
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'estimates': serializer.data,
            'total_count': queryset.count()
        })

    @action(detail=True, methods=['POST'], url_path='respond')
    def respond_to_estimate(self, request, pk=None):
        """
        견적에 대한 응답 처리
        """
        estimate = self.get_object()
        
        # 응답 데이터 검증 및 처리
        status_value = request.data.get('status')
        response_details = request.data.get('response_details', {})
        
        if not status_value:
            return Response(
                {'error': '상태 값이 필요합니다.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        estimate.status = status_value
        # 추가 로직 구현 가능 (예: response_details 저장)
        estimate.save()
        
        serializer = self.get_serializer(estimate)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReceivedEstimateViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        받은 견적 목록 조회
        """
        try:
            # 현재 로그인한 Provider의 ID 사용
            provider_user_id = request.user.id
            
            # 쿼리 파라미터 추출
            params = {
                'provider_user_id': provider_user_id,
                'status': request.query_params.get('status', ''),
                'search': request.query_params.get('search', '')
            }

            # 공통 API 서버에서 견적 데이터 요청
            response = requests.get(
                f"{settings.COMMON_API_URL}/estimates/received/", 
                params=params,
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )

            # 응답 처리
            if response.status_code == 200:
                estimates_data = response.json().get('estimates', [])
                serializer = ReceivedEstimateSerializer(estimates_data, many=True)
                
                return Response({
                    'estimates': serializer.data,
                    'total_count': len(serializer.data)
                })
            else:
                return Response(
                    {
                        'estimates': [],
                        'error': f'API 요청 실패: {response.status_code}',
                        'detail': response.text
                    }, 
                    status=response.status_code
                )

        except requests.RequestException as e:
            return Response(
                {
                    'estimates': [],
                    'error': '네트워크 오류 발생',
                    'detail': str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """
        특정 견적 상세 조회
        """
        try:
            response = requests.get(
                f"{settings.COMMON_API_URL}/estimates/{pk}/", 
                headers={'Accept': 'application/json'}
            )

            if response.status_code == 200:
                estimate_data = response.json()
                serializer = ReceivedEstimateSerializer(estimate_data)
                return Response(serializer.data)
            elif response.status_code == 404:
                return Response(
                    {'error': '해당 견적을 찾을 수 없습니다.'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            else:
                return Response(
                    {'error': '견적 상세 정보를 불러오는 중 오류가 발생했습니다.'}, 
                    status=response.status_code
                )

        except requests.RequestException as e:
            return Response(
                {'error': f'네트워크 오류: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['POST'], url_path='respond')
    def respond_to_estimate(self, request, pk=None):
        """
        견적에 대한 응답 처리
        """
        try:
            # 공통 API 서버에 응답 전달
            response = requests.post(
                f"{settings.COMMON_API_URL}/estimates/{pk}/respond/",
                json=request.data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )

            if response.status_code in [200, 201]:
                return Response(response.json(), status=response.status_code)
            else:
                return Response(
                    {'error': '견적 응답 처리 중 오류가 발생했습니다.'}, 
                    status=response.status_code
                )

        except requests.RequestException as e:
            return Response(
                {'error': f'네트워크 오류: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@permission_classes([AllowAny])  # 필요에 따라 인증 정책 조정 가능
def received_estimates(request):
    """
    받은 견적 요청 목록 조회
    """
    try:
        # provider_user_id 가져오기
        provider_user_id = request.GET.get("provider_user_id")
        status_filter = request.GET.get("status", "")
        search_term = request.GET.get("search", "")

        # provider_user_id 유효성 검사
        if not provider_user_id or not provider_user_id.isdigit():
            return Response(
                {"error": "provider_user_id가 유효하지 않습니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        provider_user_id = int(provider_user_id)

        # 견적 필터링 로직 개선
        estimates = Estimate.objects.filter(
            Q(provider_user_id=provider_user_id) |  # 명시적으로 지정된 Provider
            Q(service_categories__isnull=False)  # 서비스 카테고리가 있는 견적
        )

        # 추가 필터링 적용
        if status_filter:
            estimates = estimates.filter(status=status_filter)
        
        if search_term:
            estimates = estimates.filter(
                Q(service_category__name__icontains=search_term) | 
                Q(address__icontains=search_term)
            )

        # 중복 제거
        estimates = estimates.distinct()

        # 시리얼라이저를 사용하여 직렬화
        serializer = ReceivedEstimateSerializer(
            [
                {
                    "id": e.id,
                    "estimate_number": e.estimate_number,
                    "service_category": e.service_category.name if e.service_category else "미지정",
                    "status": e.status,
                    "address": e.address,
                    "preferred_schedule": e.get_preferred_schedule_display(),
                    "created_at": e.created_at,
                    "contact_name": e.contact_name,
                    "contact_phone": e.contact_phone,
                    "contact_email": e.contact_email,
                    "measurement_locations": [
                        {
                            "id": loc.id,
                            "name": loc.name
                        } for loc in e.measurement_locations.all()
                    ],
                    "service_categories": [
                        {
                            "code": cat.category_code,
                            "name": cat.name
                        } for cat in e.service_categories.all()
                    ],
                    "demand_user_id": e.demand_user_id,
                    "provider_user_id": e.provider_user_id
                }
                for e in estimates
            ], 
            many=True
        )

        return Response({
            "estimates": serializer.data,
            "total_count": len(serializer.data)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"API 오류 발생: {str(e)}")
        return Response({
            "error": f"서버 오류 발생: {str(e)}",
            "estimates": [],
            "total_count": 0
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

