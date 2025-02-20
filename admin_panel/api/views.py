from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from users.models import Company
from api.serializers import CompanySerializer
from django.utils import timezone

class CompanyViewSet(viewsets.ModelViewSet):
    """
    업체 관리를 위한 ViewSet
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user_type = self.request.query_params.get('user_type', None)
        status_param = self.request.query_params.get('status', None)
        
        filters = {}
        if user_type:
            filters['user_type'] = user_type
        if status_param:
            filters['status'] = status_param
            
        return queryset.filter(**filters).select_related('approved_by')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        company = self.get_object()
        company.status = 'approved'
        company.approved_at = timezone.now()
        company.approved_by = request.user
        company.save()
        
        return Response({
            'status': 'approved',
            'message': f'{company.company_name} 업체가 승인되었습니다.'
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        company = self.get_object()
        reason = request.data.get('reason', '')
        company.status = 'rejected'
        company.save()
        
        return Response({
            'status': 'rejected',
            'message': f'{company.company_name} 업체가 거부되었습니다.',
            'reason': reason
        })
