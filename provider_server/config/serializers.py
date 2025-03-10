# provider 서버에서 사용하는 시리얼라이저

from rest_framework import serializers
from users.models import ProviderUser



class ProviderUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderUser
        fields = ['id', 'username', 'email', 'company_name', 'business_registration_number', 'business_phone_number', 'address', 'address_detail', 'is_approved', 'is_active']



