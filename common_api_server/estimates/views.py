import requests
from django.conf import settings
from django.http import JsonResponse
import json
from services.models import ServiceCategory
from .models import Estimate, MeasurementLocation
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404


def get_demand_user_info(user_id):
    """Demand 서버에서 사용자 정보 가져오기"""
    url = f"{settings.DEMAND_SERVER_URL}/users/{user_id}/"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def get_provider_user_info(provider_id):
    """Provider 서버에서 사용자 정보 가져오기"""
    url = f"{settings.PROVIDER_SERVER_URL}/users/{provider_id}/"
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
            contact_email=contact_info['contact_email']
        )
        
        # 다중 카테고리 연결
        estimate.service_categories.set(categories)
        estimate.measurement_locations.add(location)

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


@csrf_exempt
def get_estimate_list(request):
    """견적 리스트 조회 API"""
    if request.method == "GET":
        provider_user_id = request.GET.get("provider_user_id")
        demand_user_id = request.GET.get("demand_user_id")
        status = request.GET.get("status")

        estimates = Estimate.get_estimates(
            provider_user_id=provider_user_id,
            demand_user_id=demand_user_id,
            status=status
        )

        result = [
            {
                "estimate_number": e.estimate_number,
                "service_category": e.service_category.name,
                "status": e.status,
                "total_amount": e.total_amount,
                "created_at": e.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for e in estimates
        ]

        return JsonResponse({"estimates": result}, status=200)

    return JsonResponse({"error": "잘못된 요청 방식입니다."}, status=405)

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