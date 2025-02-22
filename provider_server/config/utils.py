import requests
from django.conf import settings

COMMON_API_URL = settings.COMMON_API_URL  # 공통 API 서버 주소

def get_service_categories():
    """공통 API 서버에서 서비스 카테고리 데이터를 가져옴"""
    url = f"{COMMON_API_URL}/api/service-categories/"
    headers = {'Authorization': f'Token {settings.COMMON_API_TOKEN}'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()  # JSON 데이터 반환
        else:
            return []  # 실패 시 빈 리스트 반환
    except requests.RequestException:
        return []  # 요청 예외 발생 시 빈 리스트 반환
