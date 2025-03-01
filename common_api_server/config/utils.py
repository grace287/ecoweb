import requests
from django.conf import settings

def get_demand_user_info(user_id):
    """Demand 서버에서 특정 사용자 정보 가져오기"""
    url = f"{settings.DEMAND_SERVER_URL}/users/{demand_id}/"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_provider_user_info(provider_id):
    """Provider 서버에서 특정 사용자 정보 가져오기"""
    url = f"{settings.PROVIDER_SERVER_URL}/users/{provider_id}/"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

