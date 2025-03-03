from django.contrib import admin
from .models import Payment, PaymentRefund

# Register your models here.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'estimate_id', 
        'payment_method', 
        'amount', 
        'status',
        'is_paid', 
        'created_at'
    )
    list_filter = ('status', 'payment_method', 'is_paid')
    search_fields = ('id', 'estimate_id', 'pg_transaction_id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'paid_at')
    fieldsets = (
        ('기본 정보', {
            'fields': ('estimate_id', 'payment_method', 'status')
        }),
        ('금액 정보', {
            'fields': ('amount', 'vat_amount', 'total_amount')
        }),
        ('결제 상태', {
            'fields': ('is_paid', 'paid_at')
        }),
        ('PG사 정보', {
            'fields': ('pg_transaction_id', 'payment_key')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    list_display = ('refund_number', 'payment', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('refund_number', 'payment__id')
    readonly_fields = ('refund_number', 'created_at', 'completed_at')


