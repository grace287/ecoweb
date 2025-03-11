from rest_framework import serializers
from .models import (
    Estimate, 
    MeasurementLocation, 
    MeasurementItem, 
    EstimateAttachment
)
from services.models import ServiceCategory
from estimates.models import ReceivedEstimate
# from users.models import ProviderUser

class ServiceCategorySerializer(serializers.ModelSerializer):
    """서비스 카테고리 시리얼라이저"""
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'category_code']

class MeasurementLocationSerializer(serializers.ModelSerializer):
    """측정 장소 시리얼라이저"""
    class Meta:
        model = MeasurementLocation
        fields = ['id', 'name']

class MeasurementItemSerializer(serializers.ModelSerializer):
    """측정 항목 시리얼라이저"""
    category = ServiceCategorySerializer(read_only=True)

    class Meta:
        model = MeasurementItem
        fields = [
            'id', 
            'category', 
            'unit_price', 
            'maintain_quantity', 
            'recommend_quantity', 
            'subtotal'
        ]

class EstimateAttachmentSerializer(serializers.ModelSerializer):
    """견적 첨부파일 시리얼라이저"""
    class Meta:
        model = EstimateAttachment
        fields = [
            'id', 
            'file_type', 
            'file', 
            'uploaded_at'
        ]

class EstimateSerializer(serializers.ModelSerializer):
    """기본 견적 시리얼라이저"""
    service_category = ServiceCategorySerializer(read_only=True)
    service_categories = ServiceCategorySerializer(many=True, read_only=True)
    measurement_locations = MeasurementLocationSerializer(many=True, read_only=True)

    class Meta:
        model = Estimate
        fields = [
            'id',
            'estimate_number',
            'service_category',
            'service_categories',
            'status',
            'address',
            'preferred_schedule',
            'created_at',
            'contact_name',
            'contact_phone',
            'contact_email',
            'measurement_locations',
            'demand_user_id',
            'provider_user_id'
        ]
        read_only_fields = ['id', 'estimate_number', 'created_at']

    def to_representation(self, instance):
        """
        커스텀 직렬화 메서드로 더 풍부한 데이터 제공
        """
        representation = super().to_representation(instance)
        
        # 추가 필드 및 포맷팅
        representation['created_at'] = instance.created_at.strftime("%Y-%m-%d %H:%M:%S")
        representation['preferred_schedule_display'] = instance.get_preferred_schedule_display()
        
        # 상태에 따른 추가 정보
        status_map = {
            'REQUEST': '견적요청',
            'WORKING': '작성중',
            'RESPONSE': '견적응답',
            'APPROVED': '수락',
            'REJECTED': '거절',
            'PAID': '결제완료',
            'CANCELLED': '취소'
        }
        representation['status_display'] = status_map.get(instance.status, instance.status)
        
        return representation

class EstimateListSerializer(serializers.ModelSerializer):
    """견적 목록 시리얼라이저"""
    service_category = ServiceCategorySerializer(read_only=True)
    service_categories = ServiceCategorySerializer(many=True, read_only=True)
    measurement_locations = MeasurementLocationSerializer(many=True, read_only=True)

    class Meta:
        model = Estimate
        fields = [
            'id',
            'estimate_number',
            'demand_user_id',
            'service_category',
            'service_categories',
            'status',
            'address',
            'preferred_schedule',
            'created_at',
            'contact_name',
            'contact_phone',
            'contact_email',
            'measurement_locations',
            'demand_user_id',
            'provider_user_id',
            'is_favorited'
        ]
        read_only_fields = ['id', 'estimate_number', 'created_at']

    def to_representation(self, instance):
        """
        커스텀 직렬화 메서드로 더 풍부한 데이터 제공
        """
        representation = super().to_representation(instance)
        
        # 추가 필드 및 포맷팅
        representation['created_at'] = instance.created_at.strftime("%Y-%m-%d %H:%M:%S")
        representation['preferred_schedule_display'] = instance.get_preferred_schedule_display()
        
        # 상태에 따른 추가 정보
        status_map = {
            'REQUEST': '견적요청',
            'WORKING': '작성중',
            'RESPONSE': '견적응답',
            'APPROVED': '수락',
            'REJECTED': '거절',
            'PAID': '결제완료',
            'CANCELLED': '취소'
        }
        representation['status_display'] = status_map.get(instance.status, instance.status)
        
        return representation

class EstimateDetailSerializer(EstimateListSerializer):
    """견적 상세 시리얼라이저"""
    measurement_items = MeasurementItemSerializer(many=True, read_only=True)
    attachments = EstimateAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Estimate
        fields = EstimateListSerializer.Meta.fields + [
            'base_amount',
            'discount_amount',
            'vat_amount',
            'total_amount',
            'valid_until',
            'measurement_items',
            'attachments'
        ]

    def to_representation(self, instance):
        """
        상세 정보를 포함한 직렬화
        """
        representation = super().to_representation(instance)
        
        # 금액 정보 추가
        representation['amount_details'] = {
            'base_amount': float(instance.base_amount or 0),
            'discount_amount': float(instance.discount_amount or 0),
            'vat_amount': float(instance.vat_amount or 0),
            'total_amount': float(instance.total_amount or 0)
        }
        
        # 유효기간 포맷팅
        if instance.valid_until:
            representation['valid_until'] = instance.valid_until.strftime("%Y-%m-%d %H:%M:%S")
        
        return representation

class EstimateCreateSerializer(serializers.ModelSerializer):
    """견적 생성 시리얼라이저"""
    service_categories = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all(), 
        many=True
    )
    measurement_locations = serializers.PrimaryKeyRelatedField(
        queryset=MeasurementLocation.objects.all(), 
        many=True
    )

    class Meta:
        model = Estimate
        fields = [
            'service_category',
            'service_categories',
            'measurement_locations',
            'preferred_schedule',
            'contact_name',
            'contact_phone',
            'contact_email',
            'address',
            'base_amount',
            'discount_amount'
        ]

    def create(self, validated_data):
        """
        견적 생성 커스텀 메서드
        """
        # 다대다 관계 필드 분리
        service_categories = validated_data.pop('service_categories', [])
        measurement_locations = validated_data.pop('measurement_locations', [])

        # 견적 생성
        estimate = Estimate.objects.create(**validated_data)

        # 다대다 관계 설정
        estimate.service_categories.set(service_categories)
        estimate.measurement_locations.set(measurement_locations)

        return estimate

class ReceivedEstimateListSerializer(serializers.ModelSerializer):
    """받은 견적 목록 시리얼라이저"""
    service_category = ServiceCategorySerializer(read_only=True, source='estimate.service_category')
    service_categories = ServiceCategorySerializer(many=True, read_only=True, source='estimate.service_categories')

    class Meta:
        model = ReceivedEstimate
        fields = [
            'id',
            'estimate_number',
            'service_category',
            'service_categories',
            'status',
            'address',
            'preferred_schedule',
            'created_at',
            'contact_name',
            'contact_phone',
            'contact_email',
            'received_at'
        ]

    def to_representation(self, instance):
        """커스텀 직렬화 메서드"""
        representation = super().to_representation(instance)
        
        # Estimate의 속성 사용
        representation['estimate_number'] = instance.estimate.estimate_number
        representation['created_at'] = instance.estimate.created_at.strftime("%Y-%m-%d %H:%M:%S")
        representation['received_at'] = instance.received_at.strftime("%Y-%m-%d %H:%M:%S")
        
        # 상태 표시 매핑
        status_map = {
            'REQUEST': '견적요청',
            'WORKING': '작성중',
            'RESPONSE': '견적응답',
            'APPROVED': '수락',
            'REJECTED': '거절',
            'PAID': '결제완료',
            'CANCELLED': '취소'
        }
        representation['status_display'] = status_map.get(instance.estimate.status, instance.estimate.status)
        
        return representation

class ReceivedEstimateDetailSerializer(ReceivedEstimateListSerializer):
    """받은 견적 상세 시리얼라이저"""
    class Meta:
        model = ReceivedEstimate
        fields = ReceivedEstimateListSerializer.Meta.fields + [
            'base_amount',
            'discount_amount',
            'vat_amount',
            'total_amount',
            'valid_until',
            'measurement_locations',
            'attachments'
        ]

    def to_representation(self, instance):
        """상세 정보 포함 직렬화"""
        representation = super().to_representation(instance)
        
        # 금액 정보 추가
        representation['amount_details'] = {
            'base_amount': float(instance.base_amount or 0),
            'discount_amount': float(instance.discount_amount or 0),
            'vat_amount': float(instance.vat_amount or 0),
            'total_amount': float(instance.total_amount or 0)
        }
        
        # 유효기간 포맷팅
        if instance.valid_until:
            representation['valid_until'] = instance.valid_until.strftime("%Y-%m-%d %H:%M:%S")
        
        return representation

class ReceivedEstimateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    estimate_number = serializers.CharField()
    service_category = serializers.CharField()
    status = serializers.CharField()
    address = serializers.CharField()
    preferred_schedule = serializers.CharField()
    created_at = serializers.DateTimeField()
    contact_info = serializers.SerializerMethodField()
    measurement_locations = serializers.ListField(child=serializers.DictField())
    service_categories = serializers.ListField(child=serializers.DictField())
    demand_user_id = serializers.IntegerField()
    provider_user_id = serializers.IntegerField()

    def get_contact_info(self, obj):
        return {
            'name': obj.get('contact_name', ''),
            'phone': obj.get('contact_phone', ''),
            'email': obj.get('contact_email', '')
        }
