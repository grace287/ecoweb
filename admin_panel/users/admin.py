from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from users.models import AdminUser, Company, CompanyDocument

@admin.register(AdminUser)
class AdminUserAdmin(UserAdmin):
    """관리자 계정 관리"""
    list_display = ('username', 'email', 'phone_number', 'last_login', 'login_count')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('개인정보', {'fields': ('email', 'phone_number')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('로그인정보', {'fields': ('last_login_ip', 'login_count')}),
    )

    readonly_fields = ('last_login_ip', 'login_count')

    def has_add_permission(self, request):
        """관리자는 한 명만 존재할 수 있도록 제한"""
        return not AdminUser.objects.exists()


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """업체 관리"""
    list_display = (
        'company_name', 
        'user_type', 
        'business_registration_number',
        'status', 
        'created_at', 
        'approved_at'
    )
    list_filter = ('user_type', 'status')
    search_fields = ('company_name', 'business_registration_number', 'email')
    readonly_fields = ('created_at', 'updated_at', 'approved_at', 'approved_by')
    actions = ['approve_companies', 'reject_companies']

    fieldsets = (
        ('기본정보', {
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
        ('승인정보', {
            'fields': (
                'status',
                'rejection_reason',
                'approved_by',
                'approved_at',
                'created_at',
                'updated_at'
            )
        })
    )

    def approve_companies(self, request, queryset):
        """선택된 업체들을 승인 처리"""
        updated = queryset.update(
            status='approved',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated}개 업체가 승인되었습니다.')
    approve_companies.short_description = '선택된 업체 승인'

    def reject_companies(self, request, queryset):
        """선택된 업체들을 거부 처리"""
        reason = request.POST.get('rejection_reason', '')
        updated = queryset.update(
            status='rejected',
            approved_by=request.user,
            approved_at=timezone.now(),
            rejection_reason=reason
        )
        self.message_user(request, f'{updated}개 업체가 거부되었습니다.')
    reject_companies.short_description = '선택된 업체 승인거부'

    def has_add_permission(self, request):
        """업체 추가 권한 비활성화 (provider_server에서만 생성 가능)"""
        return False


@admin.register(CompanyDocument)
class CompanyDocumentAdmin(admin.ModelAdmin):
    """업체 제출 서류 관리"""
    list_display = ('company', 'document_type', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('company__company_name',)
    readonly_fields = ('uploaded_at',)

    def has_add_permission(self, request):
        """서류 추가 권한 비활성화 (provider_server에서만 생성 가능)"""
        return False
