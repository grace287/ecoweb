from django.contrib import admin
from .models import (
    MeasurementLocation,
    Estimate,
    MeasurementItem,
    EstimateAttachment
)

@admin.register(MeasurementLocation)
class MeasurementLocationAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ('estimate_number', 'contact_name', 'status', 'created_at')
    search_fields = ('estimate_number', 'contact_name', 'contact_email')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)

@admin.register(MeasurementItem)
class MeasurementItemAdmin(admin.ModelAdmin):
    list_display = ('estimate', 'category', 'unit_price', 'maintain_quantity', 'recommend_quantity', 'subtotal')
    search_fields = ('estimate__estimate_number', 'category__name')
    list_filter = ('category',)

@admin.register(EstimateAttachment)
class EstimateAttachmentAdmin(admin.ModelAdmin):
    list_display = ('estimate', 'file_type', 'uploaded_at')
    search_fields = ('estimate__estimate_number',)
    list_filter = ('file_type',)