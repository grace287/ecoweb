from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import requests
from django.conf import settings
from .models import Payment
from .serializers import PaymentSerializer

# Create your views here.

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request):
        """결제 생성"""
        # 1. 견적서 정보 확인
        estimate_id = request.data.get('estimate_id')
        try:
            # Common API 서버에서 견적서 정보 조회
            response = requests.get(
                f"{settings.COMMON_API_URL}/api/estimates/{estimate_id}/"
            )
            if response.status_code != 200:
                return Response(
                    {"error": "견적서를 찾을 수 없습니다."},
                    status=status.HTTP_404_NOT_FOUND
                )
            estimate_data = response.json()
            
            # 2. 결제 정보 생성
            payment_data = {
                'estimate_id': estimate_id,
                'amount': estimate_data['total_amount'],
                'payment_method': request.data.get('payment_method')
            }
            
            serializer = self.get_serializer(data=payment_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except requests.RequestException:
            return Response(
                {"error": "견적서 조회 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """결제 처리"""
        payment = self.get_object()
        
        if payment.is_paid:
            return Response(
                {"error": "이미 결제가 완료된 건입니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 실제 결제 처리 로직
            # PG사 연동 등의 로직이 여기에 들어갈 수 있음
            payment.complete_payment()

            # 견적서 상태 업데이트
            response = requests.put(
                f"{settings.COMMON_API_URL}/api/estimates/{payment.estimate_id}/",
                json={'status': 'PAID'}
            )
            
            if response.status_code == 200:
                return Response({
                    "message": "결제가 성공적으로 처리되었습니다.",
                    "payment": self.get_serializer(payment).data
                })
            else:
                # 결제는 성공했지만 견적서 상태 업데이트 실패
                return Response({
                    "warning": "결제는 성공했으나 견적서 상태 업데이트에 실패했습니다.",
                    "payment": self.get_serializer(payment).data
                }, status=status.HTTP_206_PARTIAL_CONTENT)

        except Exception as e:
            return Response(
                {"error": f"결제 처리 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
