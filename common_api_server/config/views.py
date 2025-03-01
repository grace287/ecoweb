from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from estimates.models import Estimate
from config.utils import get_demand_user_info, get_provider_user_info  # utils.py 활용
from django.http import HttpResponse

def home(request):
    return HttpResponse("""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Common API Server</title>
        </head>
        <body>
            <h1>common_api_server</h1>
            <p>공통 api server 입니다. 포트 : 8003</p>
            <p>공통 api 호출 앱 : estimates(견적), services(서비스), chat(채팅)</p>
        </body>
        </html>
    """)


def estimate_detail(request, estimate_id):
    """견적서 상세 정보 제공"""
    estimate = get_object_or_404(Estimate, id=estimate_id)

    # 🔹 Demand 서버에서 사용자 정보 가져오기
    demand_user_info = get_demand_user_info(estimate.demand_user_id)

    # 🔹 Provider 서버에서 사용자 정보 가져오기
    provider_user_info = get_provider_user_info(estimate.provider_user_id) if estimate.provider_user_id else None

    data = {
        "estimate_number": estimate.estimate_number,
        "service_category": list(estimate.service_category.values_list("name", flat=True)),
        "base_amount": estimate.base_amount,
        "discount_amount": estimate.discount_amount,
        "vat_amount": estimate.vat_amount,
        "total_amount": estimate.total_amount,
        "status": estimate.status,
        "created_at": estimate.created_at,
        "updated_at": estimate.updated_at,
        "demand_user": demand_user_info,
        "provider_user": provider_user_info,
    }
    return JsonResponse(data)
