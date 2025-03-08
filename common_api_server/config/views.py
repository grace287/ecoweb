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


# def estimate_detail(request, estimate_id):
#     """견적서 상세 정보 제공"""
#     estimate = get_object_or_404(Estimate, id=estimate_id)

#     # 🔹 Demand 서버에서 사용자 정보 가져오기
#     demand_user_info = get_demand_user_info(estimate.demand_user_id)

#     # 🔹 Provider 서버에서 사용자 정보 가져오기
#     provider_user_info = get_provider_user_info(estimate.provider_user_id) if estimate.provider_user_id else None

#     data = {
#         "estimate_number": estimate.estimate_number,
#         "service_category": list(estimate.service_category.values_list("name", flat=True)),
#         "base_amount": estimate.base_amount,
#         "discount_amount": estimate.discount_amount,
#         "vat_amount": estimate.vat_amount,
#         "total_amount": estimate.total_amount,
#         "status": estimate.status,
#         "created_at": estimate.created_at,
#         "updated_at": estimate.updated_at,
#         "demand_user": demand_user_info,
#         "provider_user": provider_user_info,
#     }
#     return JsonResponse(data)

def received_estimates(request):
    """✅ Provider 서버에서 받은 견적 요청 목록 조회"""
    try:
        provider_user_id = request.GET.get("provider_user_id")
        status = request.GET.get("status", "")
        search_term = request.GET.get("search", "")

        # 필수 파라미터 확인
        if not provider_user_id:
            return Response({"error": "provider_user_id가 필요합니다."}, status=400)

        # 📝 필터링 조건 설정
        estimates = Estimate.objects.filter(provider_user_id=provider_user_id)

        if status:
            estimates = estimates.filter(status=status)

        if search_term:
            estimates = estimates.filter(
                Q(service_category__name__icontains=search_term) |
                Q(address__icontains=search_term)
            )

        # ✅ JSON 응답 데이터 구성
        result = [
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
                "measurement_locations": [loc.name for loc in e.measurement_locations.all()],
                "service_categories": [cat.name for cat in e.service_categories.all()]
            }
            for e in estimates
        ]

        return Response({"estimates": result}, status=200)

    except Exception as e:
        print(f"❌ API 오류 발생: {str(e)}")
        return Response({"error": f"서버 오류 발생: {str(e)}"}, status=500)

