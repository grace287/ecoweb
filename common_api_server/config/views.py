from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from estimates.models import Estimate
from config.utils import get_demand_user_info, get_provider_user_info  # utils.py 활용
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

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

@csrf_exempt
def approve_request(request):
    if request.method == 'POST':
        # 요청 데이터에서 필요한 정보 추출
        provider_id = request.POST.get('provider_id')
        
        # 승인 로직 처리
        try:
            provider = get_object_or_404(Provider, id=provider_id)
            provider.status = 'approved'
            provider.save()
            return JsonResponse({'success': True, 'message': '승인되었습니다.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'})

