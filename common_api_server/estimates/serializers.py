from rest_framework import serializers
from .models import Estimate, MeasurementItem

class MeasurementItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementItem
        fields = '__all__'

class EstimateSerializer(serializers.ModelSerializer):
    measurement_items = MeasurementItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Estimate
        fields = '__all__'
