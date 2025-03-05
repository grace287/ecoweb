import requests
from django.conf import settings
from .models import DemandUser, ProviderUser, ServiceCategory

def sync_users_from_servers():
    """Demand 및 Provider 서버에서 사용자 정보 동기화"""
    # Demand 서버 사용자 동기화
    try:
        demand_response = requests.get(f"{settings.DEMAND_API_URL}/users/")
        if demand_response.status_code == 200:
            for user_data in demand_response.json():
                DemandUser.objects.update_or_create(
                    username=user_data['username'],
                    defaults={
                        'email': user_data.get('email', ''),
                        'company_name': user_data.get('company_name', ''),
                        'is_approved': user_data.get('is_approved', False)
                    }
                )
    except Exception as e:
        print(f"Demand 서버 사용자 동기화 오류: {e}")

    # Provider 서버 사용자 동기화
    try:
        provider_response = requests.get(f"{settings.PROVIDER_API_URL}/users/")
        if provider_response.status_code == 200:
            for user_data in provider_response.json():
                ProviderUser.objects.update_or_create(
                    username=user_data['username'],
                    defaults={
                        'email': user_data.get('email', ''),
                        'company_name': user_data.get('company_name', ''),
                        'business_registration_number': user_data.get('business_registration_number', ''),
                        'is_approved': user_data.get('is_approved', False)
                    }
                )
    except Exception as e:
        print(f"Provider 서버 사용자 동기화 오류: {e}")

    # 서비스 카테고리 동기화
    ServiceCategory.sync_service_categories()
