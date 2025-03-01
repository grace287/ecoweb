import requests
from django.conf import settings
from django.http import JsonResponse
import json
from services.models import ServiceCategory
from .models import Estimate
from django.views.decorators.csrf import csrf_exempt

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
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            provider_user_id = data.get("provider_user_id")
            category_code = data.get("service_category")

            # ✅ 같은 서버 내 `services` 앱에서 `ServiceCategory` 직접 조회
            try:
                service_category = ServiceCategory.objects.get(category_code=category_code)
            except ServiceCategory.DoesNotExist:
                return JsonResponse({"error": "해당 서비스 카테고리를 찾을 수 없습니다."}, status=400)

            # ✅ 견적서 생성
            estimate = Estimate.objects.create(
                provider_user_id=provider_user_id,
                service_category=service_category,  # ✅ `ForeignKey`로 연결
                total_price=data.get("total_price", 0)
            )

            return JsonResponse({"success": True, "estimate_id": estimate.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)

    return JsonResponse({"error": "잘못된 요청 방식입니다."}, status=405)



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