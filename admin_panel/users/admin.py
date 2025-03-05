from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.conf import settings
import requests
from django.utils.html import format_html

from .models import (
    AdminUser, 
    DemandUser, 
    ProviderUser, 
    Company, 
    CompanyDocument, 
    ServiceCategory
)

@admin.register(DemandUser)
class DemandUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'company_name', 'is_active', 'is_approved', 'created_at')
    list_filter = ('is_active', 'is_approved', 'created_at')
    search_fields = ('username', 'email', 'company_name')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('개인 정보', {'fields': ('email', 'company_name', 'business_phone_number', 'contact_phone_number')}),
        ('주소', {'fields': ('address', 'address_detail')}),
        ('권한', {'fields': ('is_active', 'is_approved')}),
        ('중요 날짜', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at')

@admin.register(ProviderUser)
class ProviderUserAdmin(UserAdmin):
    list_display = (
        'username', 
        'email', 
        'company_name', 
        'business_registration_number', 
        'is_active', 
        'is_approved', 
        'created_at'
    )
    list_filter = ('is_active', 'is_approved', 'created_at')
    search_fields = ('username', 'email', 'company_name', 'business_registration_number')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('업체 정보', {'fields': (
            'company_name', 
            'business_registration_number', 
            'business_phone_number', 
            'consultation_phone_number'
        )}),
        ('주소', {'fields': ('address', 'address_detail')}),
        ('권한', {'fields': ('is_active', 'is_approved')}),
        ('중요 날짜', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at')

    def get_pending_users(self, request):
        """관리자 페이지에서 대기 중인 사용자 목록 반환"""
        pending_users = ProviderUser.objects.filter(is_approved=False)
        return pending_users

    def changelist_view(self, request, extra_context=None):
        """대기 중인 사용자 목록을 컨텍스트에 추가"""
        extra_context = extra_context or {}
        extra_context['pending_users'] = self.get_pending_users(request)
        return super().changelist_view(request, extra_context)

@admin.register(AdminUser)
class AdminUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'last_login', 'is_active')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('개인정보', {'fields': ('email', 'phone_number')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('로그인정보', {'fields': ('last_login_ip', 'login_count')}),
    )

    readonly_fields = ('last_login_ip', 'login_count')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        'company_name', 
        'user_type', 
        'business_registration_number',
        'status', 
        'created_at',
        'approved_at'
    )
    list_filter = ('user_type', 'status', 'created_at')
    search_fields = ('company_name', 'business_registration_number', 'email')
    
    fieldsets = (
        ('기본 정보', {
            'fields': (
                'username', 
                'email', 
                'company_name', 
                'user_type', 
                'business_registration_number'
            )
        }),
        ('연락처', {
            'fields': (
                'business_phone_number', 
                'consultation_phone_number'
            )
        }),
        ('주소', {
            'fields': (
                'address', 
                'address_detail'
            )
        }),
        ('상태', {
            'fields': (
                'status', 
                'approved_by', 
                'approved_at', 
                'rejection_reason'
            )
        })
    )

    readonly_fields = ('created_at', 'updated_at', 'approved_at')

@admin.register(CompanyDocument)
class CompanyDocumentAdmin(admin.ModelAdmin):
    list_display = ('company', 'document_type', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('company__company_name',)
    readonly_fields = ('uploaded_at',)

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_code', 'name')
    search_fields = ('category_code', 'name')
    actions = ['sync_categories']

    def sync_categories(self, request, queryset):
        """서비스 카테고리 동기화 액션"""
        result = ServiceCategory.sync_service_categories()
        if result:
            self.message_user(request, "서비스 카테고리가 성공적으로 동기화되었습니다.")
        else:
            self.message_user(request, "서비스 카테고리 동기화에 실패했습니다.", level='error')
    
    sync_categories.short_description = "서비스 카테고리 동기화"
