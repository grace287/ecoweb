# serializers.py (권장 위치: users/serializers.py)

from rest_framework import serializers
from users.models import DemandUser
from django.contrib.auth import authenticate

class SignupSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = DemandUser
        fields = ['username', 'email', 'password', 'password_confirm', 'company_name', 'business_phone_number', 'address', 'address_detail', 'recommend_id']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = DemandUser(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = True
        user.is_approved = True
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("아이디 또는 비밀번호가 올바르지 않습니다.")
        data['user'] = user
        return data


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandUser
        fields = ['username', 'email', 'company_name', 'business_phone_number', 'address', 'address_detail', 'region', 'industry']

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    new_password_confirm = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("새 비밀번호가 일치하지 않습니다.")
        return data
