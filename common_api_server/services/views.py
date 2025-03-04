from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from services.models import ServiceCategory
from estimates.models import MeasurementLocation

@csrf_exempt
def service_category_list(request):
    """✅ 서비스 카테고리 목록 API"""
    try:
        categories = ServiceCategory.objects.all().values("category_code", "name", "description")
        return JsonResponse(list(categories), safe=False, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({"error": f"서비스 카테고리 조회 중 오류 발생: {str(e)}"}, status=500)


def get_default_service_category():
    """✅ 첫 번째 서비스 카테고리를 기본값으로 가져오기"""
    try:
        category = ServiceCategory.objects.first()
        return category.id if category else None
    except ServiceCategory.DoesNotExist:
        return None  # 예외가 발생하면 None 반환

@csrf_exempt
def get_service_categories(request):
    """✅ 서비스 카테고리 목록 조회 API"""
    try:
        categories = ServiceCategory.objects.all()
        if not categories.exists():
            return JsonResponse({"categories": [], "message": "등록된 카테고리가 없습니다."}, status=200)

        data = [{
            'code': category.category_code,
            'name': category.name,
            'description': category.description,
            'icon': f'/static/img/main/category/{category.category_code}.png'
        } for category in categories]

        return JsonResponse({"categories": data}, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        return JsonResponse({"error": f"카테고리 조회 실패: {str(e)}"}, status=500)

