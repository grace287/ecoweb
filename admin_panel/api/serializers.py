from rest_framework import serializers
from users.models import Company

class CompanySerializer(serializers.ModelSerializer):
    """
    업체 정보 시리얼라이저
    """
    approved_by_name = serializers.CharField(
        source='approved_by.username', 
        read_only=True,
        allow_null=True
    )
    status_display = serializers.CharField(
        source='get_status_display', 
        read_only=True
    )
    user_type_display = serializers.CharField(
        source='get_user_type_display', 
        read_only=True
    )

    class Meta:
        model = Company
        fields = [
            'id', 
            'username', 
            'email', 
            'company_name',
            'business_registration_number',
            'business_phone_number',
            'consultation_phone_number',
            'address',
            'address_detail', 
            'user_type',
            'user_type_display',
            'status',
            'status_display',
            'created_at',
            'approved_at',
            'approved_by_name'
        ]
        read_only_fields = [
            'created_at',
            'approved_at',
            'approved_by_name',
            'status_display',
            'user_type_display'
        ]