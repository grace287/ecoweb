import requests
from django.conf import settings

DEMAND_SERVER_URL = settings.DEMAND_API_URL

def get_demand_user_info(user_id):
    """demand_server의 API를 호출하여 유저 정보를 가져옴"""
    response = requests.get(f"{DEMAND_SERVER_URL}/users/{user_id}/")
    if response.status_code == 200:
        return response.json()  # JSON 데이터 반환
    return None

PROVIDER_SERVER_URL = settings.PROVIDER_API_URL

def get_provider_user_info(user_id):
    """provider_server의 API를 호출하여 유저 정보를 가져옴"""
    response = requests.get(f"{PROVIDER_SERVER_URL}/users/{user_id}/")
    if response.status_code == 200:
        return response.json()  # JSON 데이터 반환
    return None
