from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from services.models import ServiceCategory

def service_category_list(request):
    """서비스 카테고리 목록 API"""
    categories = ServiceCategory.objects.all().values("category_code", "name", "description")
    return JsonResponse(list(categories), safe=False)

def get_default_service_category():
    category = ServiceCategory.objects.first()  # ✅ 첫 번째 카테고리 가져오기
    return category.id if category else None  # ✅ 존재하면 id 반환, 없으면 None