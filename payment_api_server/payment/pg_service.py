import requests
from django.conf import settings

class TossPaymentsService:
    def __init__(self):
        self.api_key = settings.TOSS_PAYMENTS_API_KEY
        self.api_secret = settings.TOSS_PAYMENTS_API_SECRET
        self.base_url = "https://api.tosspayments.com/v1"

    def create_payment(self, payment_data):
        """결제 생성"""
        endpoint = f"{self.base_url}/payments"
        headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "amount": payment_data['amount'],
            "orderId": f"ORDER_{payment_data['estimate_id']}",
            "orderName": f"견적서 #{payment_data['estimate_id']} 결제",
            "successUrl": f"{settings.SITE_URL}/payments/success",
            "failUrl": f"{settings.SITE_URL}/payments/fail",
            "methodType": payment_data['payment_method']
        }
        
        response = requests.post(endpoint, json=payload, headers=headers)
        return response.json()

    def confirm_payment(self, payment_key):
        """결제 승인"""
        endpoint = f"{self.base_url}/payments/{payment_key}"
        headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(endpoint, headers=headers)
        return response.json()
