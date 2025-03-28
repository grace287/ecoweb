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
from django.db import transaction  # transaction 모듈 추가
from django.utils import timezone
from django.core.paginator import Paginator

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



@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def create_estimate(request):
    """견적서 생성 API"""
    try:
        data = json.loads(request.body)
        logger.info(f"📝 요청 데이터: {data}")

        # 필수 필드 검증
        required_fields = ['service_category_codes', 'measurement_location_id', 'address', 'preferred_schedule']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return JsonResponse({
                "error": f"필수 항목이 누락되었습니다: {', '.join(missing_fields)}"
            }, status=400)

        with transaction.atomic():
            # 1. 서비스 카테고리 조회
            categories = ServiceCategory.objects.filter(
                category_code__in=data['service_category_codes']
            )
            if not categories.exists():
                return JsonResponse({
                    "error": "유효하지 않은 서비스 카테고리입니다."
                }, status=400)

            # 2. 측정 장소 조회
            try:
                location = MeasurementLocation.objects.get(id=data['measurement_location_id'])
            except MeasurementLocation.DoesNotExist:
                return JsonResponse({
                    "error": "유효하지 않은 측정 장소입니다."
                }, status=400)

            # 3. 견적서 생성
            contact_info = data.get('contact_info', {}) or {}
            estimate = Estimate.objects.create(
                service_category=categories.first(),  # 첫 번째 카테고리를 기본값으로
                address=data['address'],
                preferred_schedule=data['preferred_schedule'],
                status='REQUEST',
                contact_name=contact_info.get('name', '미지정'),
                contact_phone=contact_info.get('phone', ''),
                contact_email=contact_info.get('email', ''),
                demand_user_id=request.user.id if request.user.is_authenticated else None,  # demand_user → demand_user_id로 수정
                provider_user_id=request.user.id if request.user.is_authenticated else None  # demand_user → demand_user_id로 수정
            )


            # 4. 다중 카테고리 및 측정 장소 연결
            estimate.service_categories.set(categories)
            estimate.measurement_locations.add(location)

            logger.info(f"✅ 견적서 생성 완료: ID={estimate.id}")

            return JsonResponse({
                "success": True,
                "estimate_id": estimate.id,
                "estimate_number": estimate.estimate_number,
                "message": "견적 요청이 성공적으로 생성되었습니다."
            }, status=201)

    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON 파싱 오류: {str(e)}")
        return JsonResponse({
            "error": "잘못된 JSON 형식입니다."
        }, status=400)
    except Exception as e:
        logger.error(f"❌ 예상치 못한 오류: {str(e)}", exc_info=True)
        return JsonResponse({
            "error": str(e)
        }, status=500)
# @api_view(['POST'])
# @csrf_exempt
# @permission_classes([AllowAny])
# def create_estimate(request):
#     """견적서 생성 API"""

#     try:
#         # ✅ JSON 데이터 파싱 예외 처리
#         try:
#             data = json.loads(request.body)
#             logger.info(f"수신된 데이터: {data}")
#         except json.JSONDecodeError:
#             return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)
        
#         # 필수 필드 검증
#         required_fields = ['service_category_codes', 'measurement_location_id', 'address', 'preferred_schedule']
#         for field in required_fields:
#             if not data.get(field):
#                 return JsonResponse({"error": f"{field}는 필수 항목입니다."}, status=400)
            

#         # Provider 서버로 견적 전달
#         # provider_response = forward_estimate_to_provider(estimate)

#         # 2. 서비스 카테고리 검증
#         try:
#             categories = ServiceCategory.objects.filter(
#                 category_code__in=data['service_category_codes']
#             )
#             if not categories.exists():
#                 return JsonResponse({
#                     "error": "유효하지 않은 서비스 카테고리입니다."
#                 }, status=400)
#         except Exception as e:
#             logger.error(f"카테고리 검증 오류: {str(e)}")
#             return JsonResponse({
#                 "error": "서비스 카테고리 처리 중 오류가 발생했습니다."
#             }, status=400)

#         # 3. 측정 장소 검증
#         try:
#             location = MeasurementLocation.objects.get(id=data['measurement_location_id'])
#         except MeasurementLocation.DoesNotExist:
#             return JsonResponse({
#                 "error": "유효하지 않은 측정 장소입니다."
#             }, status=400)
#         except Exception as e:
#             logger.error(f"측정 장소 검증 오류: {str(e)}")
#             return JsonResponse({
#                 "error": "측정 장소 처리 중 오류가 발생했습니다."
#             }, status=400)

#         # 담당자 정보 처리
#         contact_info = {
#             'contact_name': '미지정',
#             'contact_phone': '',
#             'contact_email': '',
#             'demand_user_id': None
#         }

#         # 로그인된 사용자의 경우 기본 정보 추가
#         if request.user.is_authenticated:
#             contact_info.update({
#                 'demand_user_id': request.user.id,
#                 'contact_name': request.user.name if hasattr(request.user, 'name') else request.user.username,
#                 'contact_email': request.user.email
#             })

#         # 사용자가 직접 입력한 담당자 정보가 있다면 우선 적용
#         if data.get('contact_info'):
#             contact_info.update({
#                 'contact_name': data['contact_info'].get('name', contact_info['contact_name']),
#                 'contact_phone': data['contact_info'].get('phone', contact_info['contact_phone']),
#                 'contact_email': data['contact_info'].get('email', contact_info['contact_email'])
#             })

#         # 견적서 생성
#         # 첫 번째 카테고리를 기본 카테고리로 설정
#         primary_category = categories.first()
        
#         estimate = Estimate.objects.create(
#             service_category=primary_category,  # 첫 번째 카테고리를 기본으로 설정
#             address=data['address'],
#             preferred_schedule=data.get('preferred_schedule', 'asap'),
#             status='REQUEST',
#             demand_user_id=contact_info['demand_user_id'],
#             contact_name=contact_info['contact_name'],
#             contact_phone=contact_info['contact_phone'],
#             contact_email=contact_info['contact_email'],
#             provider_user_id=data.get('provider_user_id')
#         )
        
#         # 다중 카테고리 연결
#         estimate.service_categories.set(categories)
#         estimate.measurement_locations.add(location)

#         # 새로 추가: Provider 서버로 견적 전달
#         provider_response = forward_estimate_to_provider(estimate)

#         # Provider 서버 전달 결과에 따른 처리
#         if provider_response is None:
#             # Provider 서버 전달 실패 시 로깅
#             print(f"⚠️ 견적 {estimate.id}의 Provider 서버 전달 실패")
#             # 필요하다면 estimate의 상태를 업데이트하거나 추가 처리 가능


#         return JsonResponse({
#             "success": True,
#             "estimate_id": estimate.id,
#             "estimate_number": estimate.estimate_number,
#             "message": "견적 요청이 성공적으로 생성되었습니다.",
#             "contact_info": {
#                 "name": contact_info['contact_name'],
#                 "phone": contact_info['contact_phone'],
#                 "email": contact_info['contact_email']
#             }
#         }, status=201)

#     except json.JSONDecodeError:
#         return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

@api_view(['GET'])
def forward_estimate_to_provider(estimate):
    """공통 API 서버에서 Provider 서버로 견적 요청을 전달하는 함수"""
    try:
        PROVIDER_API_URL = settings.PROVIDER_API_URL  # settings에서 URL 가져오기
        provider_url = f"{PROVIDER_API_URL}/estimates/received/"
        
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
    def respond_to_estimate(self, request, estimate_id=None):
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
    

    # retrive 상세견적
    @action(detail=True, methods=['GET'], url_path='received/<int:estimate_id>/')
    def received_estimate_detail(self, request, estimate_id=None):
        """
        받은 견적 상세 조회
        """
        estimate = self.get_object()
        
        serializer = self.get_serializer(estimate)
        return Response(serializer.data, status=status.HTTP_200_OK)

def get_estimate_params(request):
    """견적 요청 파라미터 표준화"""
    return {
        'provider_user_id': request.user.id,
        'status': request.GET.get('status', ''),
        'search': request.GET.get('search', ''),
        'page': request.GET.get('page', 1),
        'page_size': request.GET.get('page_size', 10),
        'sort_by': request.GET.get('sort_by', 'created_at'),
        'sort_order': request.GET.get('sort_order', 'desc'),
        'is_favorited': request.GET.get('status') == 'FAVORITE',
        'include_customer_info': True
    }
def handle_api_response(response, default_message="API 요청 실패"):
    """API 응답 표준 처리 함수"""
    try:
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API 요청 오류: {response.status_code} - {response.text}")
            return {
                'error': True,
                'status_code': response.status_code,
                'message': default_message,
                'details': response.text
            }
    except ValueError as e:
        logger.error(f"JSON 파싱 오류: {e}")
        return {
            'error': True,
            'message': 'JSON 응답 파싱 실패',
            'details': str(e)
        }
    
def process_estimate_data(estimates_data):
    """견적 데이터 후처리 함수"""
    processed_estimates = []
    for estimate in estimates_data.get('estimates', []):
        # 추가 데이터 가공 로직
        estimate['formatted_created_at'] = format_date(estimate.get('created_at'))
        estimate['total_amount_formatted'] = format_currency(estimate.get('total_amount'))
        processed_estimates.append(estimate)

    return {
        'estimates': processed_estimates,
        'total_count': estimates_data.get('total_count', 0),
        'status_counts': calculate_status_counts(processed_estimates),
        'pagination': {
            'current_page': estimates_data.get('page', 1),
            'total_pages': estimates_data.get('total_pages', 1),
            'page_size': estimates_data.get('page_size', 10)
        }
    }

def calculate_status_counts(estimates):
    """상태별 견적 개수 계산"""
    status_counts = {
        'REQUEST': sum(1 for e in estimates if e.get('status') == 'REQUEST'),
        'RESPONSE': sum(1 for e in estimates if e.get('status') == 'RESPONSE'),
        'APPROVED': sum(1 for e in estimates if e.get('status') == 'APPROVED'),
        'REJECTED': sum(1 for e in estimates if e.get('status') == 'REJECTED'),
        'FAVORITE': sum(1 for e in estimates if e.get('is_favorited'))
    }
    return status_counts
    
@api_view(['GET'])
@permission_classes([AllowAny])
def received_estimates(request):
    """받은 견적 요청 목록 조회"""
    try:
        # 공통 필터링 로직
        queryset = Estimate.objects.filter(
            Q(provider_user_id=request.user.id) |  
            Q(service_categories__isnull=False)  
        )

        # 파라미터 기반 필터링
        status_filter = request.GET.get("status")
        search_term = request.GET.get("search")
        is_favorited = request.GET.get("is_favorited", False)

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if search_term:
            queryset = queryset.filter(
                Q(service_category__name__icontains=search_term) | 
                Q(address__icontains=search_term)
            )

        if is_favorited:
            queryset = queryset.filter(is_favorited=True)

        # 고객 정보 추가 및 데이터 인리치먼트
        enriched_estimates = []
        for estimate in queryset:
            customer_info = get_demand_user_info(estimate.demand_user_id) if estimate.demand_user_id else None
            
            enriched_estimate = {
                "id": estimate.id,
                "estimate_number": estimate.estimate_number,
                "service_category": estimate.service_category.name if estimate.service_category else "미지정",
                "status": estimate.status,
                "address": estimate.address,
                "preferred_schedule": estimate.get_preferred_schedule_display(),
                "created_at": estimate.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "measurement_locations": [
                    {"id": loc.id, "name": loc.name} for loc in estimate.measurement_locations.all()
                ],
                "service_categories": [
                    {"code": cat.category_code, "name": cat.name} for cat in estimate.service_categories.all()
                ],
                "demand_user_id": estimate.demand_user_id,
                "is_favorited": estimate.is_favorited,
                "customer_info": customer_info
            }
            enriched_estimates.append(enriched_estimate)

        # 상태별 개수 계산
        status_counts = {
            'REQUEST': sum(1 for e in enriched_estimates if e['status'] == 'REQUEST'),
            'RESPONSE': sum(1 for e in enriched_estimates if e['status'] == 'RESPONSE'),
            'APPROVED': sum(1 for e in enriched_estimates if e['status'] == 'APPROVED'),
            'REJECTED': sum(1 for e in enriched_estimates if e['status'] == 'REJECTED'),
            'FAVORITE': sum(1 for e in enriched_estimates if e['is_favorited'])
        }

        return Response({
            "estimates": enriched_estimates,
            "total_count": len(enriched_estimates),
            "status_counts": status_counts
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"받은 견적 목록 조회 중 오류: {e}", exc_info=True)
        return Response({
            'estimates': [],
            'error': f'API 요청 실패: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def estimate_detail(request, estimate_id):
    """견적서 상세 정보 조회"""
    try:
        # 견적서 조회
        estimate = get_object_or_404(Estimate, id=estimate_id)
        
        # 고객 정보 조회
        customer_info = get_demand_user_info(estimate.demand_user_id) if estimate.demand_user_id else None
        
        # 상세 정보 직렬화
        estimate_data = {
            'id': estimate.id,
            'estimate_number': estimate.estimate_number,
            'service_categories': [
                {
                    'code': cat.category_code,
                    'name': cat.name
                } for cat in estimate.service_categories.all()
            ],
            'measurement_locations': [
                {
                    'id': loc.id,
                    'name': loc.name
                } for loc in estimate.measurement_locations.all()
            ],
            'address': estimate.address,
            'preferred_schedule': estimate.get_preferred_schedule_display(),
            'status': estimate.status,
            'contact_name': estimate.contact_name,
            'contact_phone': estimate.contact_phone,
            'contact_email': estimate.contact_email,
            'demand_user_id': estimate.demand_user_id,
            'created_at': estimate.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'customer_info': customer_info,
            'base_amount': estimate.base_amount,
            'discount_amount': estimate.discount_amount,
            'total_amount': estimate.base_amount - estimate.discount_amount if estimate.base_amount and estimate.discount_amount else None
        }
        
        return Response(estimate_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"견적서 상세 조회 중 오류: {e}", exc_info=True)
        return Response({
            'error': '견적서 조회 중 오류가 발생했습니다.',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from rest_framework.decorators import authentication_classes

@api_view(['POST'])
@permission_classes([AllowAny])  # 임시로 모든 요청 허용
@authentication_classes([])      # ✅ 인증 비활성화 명시적으로 추가
@csrf_exempt                     # ✅ CSRF도 제거
def create_or_update_estimate(request, pk):
    try:
        data = request.data
        estimate = Estimate.objects.filter(id=pk).first()

        if estimate:
            serializer = EstimateSerializer(estimate, data=data, partial=True)
        else:
            data['id'] = pk  # 이 부분이 핵심
            serializer = EstimateSerializer(data=data)

        if serializer.is_valid():
            saved = serializer.save()
            return Response({
                'success': True,
                'message': '견적이 저장되었습니다.',
                'estimate_id': saved.id
            })
        return Response({'success': False, 'errors': serializer.errors}, status=400)

    except Exception as e:
        logger.error(f"견적 저장 오류: {e}", exc_info=True)
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def estimate_send(request, pk):
    """견적서 발송 처리"""
    try:
        # 1. 기존 견적 조회
        estimate = get_object_or_404(Estimate, id=pk)
        
        # 2. 견적서 데이터 업데이트
        data = request.data
        logger.info(f"수신된 견적서 데이터: {data}")

        # 견적서 업데이트
        estimate.writer_name = data.get('writer_name')
        estimate.writer_email = data.get('writer_email')
        estimate.maintain_points = data.get('maintain_points', 0)
        estimate.recommend_points = data.get('recommend_points', 0)
        estimate.unit_price = data.get('unit_price', 0)
        estimate.discount_amount = data.get('discount_amount', 0)
        estimate.total_amount = data.get('total_amount', 0)
        estimate.notes = data.get('notes')
        estimate.status = 'SENT'
        estimate.sent_at = timezone.now()
        estimate.save()

        return JsonResponse({
            'success': True,
            'message': '견적서가 성공적으로 발송되었습니다.',
            'estimate_id': estimate.id
        })

    except Estimate.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '견적을 찾을 수 없습니다.'
        }, status=404)
    
    except Exception as e:
        logger.error(f"견적서 발송 처리 중 오류: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

from rest_framework import status  # 반드시 있어야 함

@api_view(['GET'])
@permission_classes([AllowAny])  # 필요시 IsAuthenticated로 강화
def demand_estimate_list(request):
    """견적 요청 + 받은 견적 목록 API"""
    try:
        # 🟡 로그인 유저 ID를 기준으로 조회
        demand_user_id = getattr(request.user, 'id', None)

        status_filter = request.GET.get('status')
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))

        queryset = Estimate.objects.filter(
            demand_user_id=demand_user_id
        ).select_related('service_category').prefetch_related(
            'measurement_locations', 'service_categories'
        ).order_by('-created_at')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        else:
            queryset = queryset.filter(status__in=['REQUEST', 'SENT'])  # ✅ 기본 필터 추가

        logger.info(f"[ESTIMATE_LIST] demand_user_id={demand_user_id}, status={status_filter}, count={queryset.count()}")

        if search:
            queryset = queryset.filter(
                Q(service_categories__name__icontains=search) |
                Q(measurement_locations__name__icontains=search) |
                Q(address__icontains=search)
            ).distinct()

        paginator = Paginator(queryset, page_size)
        current_page = paginator.get_page(page)

        estimates_data = [{
            'id': e.id,
            'estimate_number': e.estimate_number,
            'service_category_name': e.service_category.name if e.service_category else '',
            'measurement_location_name': e.measurement_locations.first().name if e.measurement_locations.exists() else '',
            'status': e.status,
            'status_display': e.get_status_display(),
            'created_at': e.created_at.strftime('%Y-%m-%d'),
            'address': e.address,
            'total_amount': getattr(e, 'total_amount', 0),
            'estimate_count': getattr(e, 'estimate_count', 0),
            'view_count': getattr(e, 'views', 0)
        } for e in current_page]

        status_counts = {
            'REQUEST': queryset.filter(status='REQUEST').count(),
            'RESPONSE': queryset.filter(status='RESPONSE').count(),
            'APPROVED': queryset.filter(status='APPROVED').count(),
            'REJECTED': queryset.filter(status='REJECTED').count()
        }

        return Response({
            'estimates': estimates_data,
            'total_count': queryset.count(),
            'status_counts': status_counts,
            'has_next': current_page.has_next(),
            'has_previous': current_page.has_previous(),
            'current_page': page
        }, status=200)

    except Exception as e:
        logger.exception("견적 목록 조회 실패")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def demand_request_detail(request, pk):
    """보낸 견적 요청 상세 조회"""
    try:
        estimate = get_object_or_404(Estimate.objects.prefetch_related(
            'service_categories',  # ManyToMany 관계
            'measurement_locations'
        ), id=pk)
        
        estimate_data = {
            'id': estimate.id,
            'estimate_number': estimate.estimate_number,
            # 서비스 카테고리 수정
            'service_categories': [
                {
                    'id': category.id,
                    'name': category.name
                } for category in estimate.service_categories.all()
            ],
            # 측정 장소 수정
            'measurement_location': {
                'id': estimate.measurement_locations.first().id,
                'name': estimate.measurement_locations.first().name
            } if estimate.measurement_locations.exists() else None,
            'address': estimate.address,
            'preferred_schedule': estimate.preferred_schedule,
            'status': estimate.status,
            'contact_name': estimate.contact_name,
            'contact_phone': estimate.contact_phone,
            'contact_email': estimate.contact_email,
            'created_at': estimate.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        return Response(estimate_data, status=status.HTTP_200_OK)

    except Estimate.DoesNotExist:
        return Response({"error": "견적을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"견적 상세 조회 중 오류: {e}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def demand_response_detail(request, pk):
    """받은 견적 상세 조회"""
    try:
        estimate = get_object_or_404(Estimate, id=pk)
        
        # 제공자 정보 조회
        provider_info = None
        if estimate.provider_user_id:
            provider_info = {
                'id': estimate.provider_user_id,
                'name': getattr(estimate, 'provider_name', ''),  # provider_name이 없을 경우 빈 문자열 반환
            }

        estimate_data = {
            'id': estimate.id,
            'estimate_number': estimate.estimate_number,
            'service_categories': [
                {'id': cat.id, 'name': cat.name}
                for cat in estimate.service_categories.all()
            ],
            'measurement_location': {
                'id': estimate.measurement_locations.first().id,
                'name': estimate.measurement_locations.first().name
            } if estimate.measurement_locations.exists() else None,
            'address': estimate.address,
            'preferred_schedule': estimate.preferred_schedule,
            'status': estimate.status,
            'total_amount': getattr(estimate, 'total_amount', 0),
            'base_amount': getattr(estimate, 'base_amount', 0),
            'discount_amount': getattr(estimate, 'discount_amount', 0),
            'provider_info': provider_info,
            'created_at': estimate.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        return Response(estimate_data, status=status.HTTP_200_OK)

    except Estimate.DoesNotExist:
        return Response({"error": "견적을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"견적 상세 조회 중 오류: {e}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)