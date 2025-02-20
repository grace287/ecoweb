from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.conf import settings
import requests
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
        'source_display',  # 출처 표시 추가
        'approved_at'
    )
    list_filter = ('user_type', 'status', 'created_at')
    search_fields = ('company_name', 'business_registration_number', 'email')
    readonly_fields = ('created_at', 'updated_at', 'approved_at', 'approved_by')
    actions = ['approve_companies', 'reject_companies', 'sync_provider_companies']

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

    def source_display(self, obj):
        return 'Provider' if getattr(obj, 'is_provider', False) else 'Admin'
    source_display.short_description = '출처'

    def get_queryset(self, request):
        """Provider 서버의 가입 신청 데이터도 함께 표시"""
        queryset = super().get_queryset(request)
        
        try:
            # Provider 서버에서 pending 상태의 업체 목록 가져오기
            response = requests.get(
                f"{settings.PROVIDER_API_URL}/api/companies/pending/",
                headers={
                    'Authorization': f'Token {settings.PROVIDER_API_KEY}',
                    'Content-Type': 'application/json'
                },
                timeout=5
            )
            
            if response.status_code == 200:
                provider_companies = response.json()
                
                # Provider 업체 데이터를 Company 모델 형식으로 변환
                for company_data in provider_companies:
                    company_data['is_provider'] = True
                    if not queryset.filter(business_registration_number=company_data['business_registration_number']).exists():
                        Company.objects.get_or_create(
                            business_registration_number=company_data['business_registration_number'],
                            defaults={
                                'company_name': company_data['company_name'],
                                'user_type': company_data['user_type'],
                                'email': company_data['email'],
                                'business_phone_number': company_data['business_phone_number'],
                                'status': 'pending',
                                'created_at': timezone.now()
                            }
                        )
                
        except requests.RequestException as e:
            self.message_user(request, f'Provider 서버 연동 중 오류 발생: {str(e)}', level='ERROR')

        return queryset

    def approve_companies(self, request, queryset):
        """선택된 업체들을 승인 처리"""
        for company in queryset:
            if getattr(company, 'is_provider', False):
                # Provider 서버 업체 승인
                try:
                    response = requests.post(
                        f"{settings.PROVIDER_API_URL}/api/companies/{company.id}/approve/",
                        headers={
                            'Authorization': f'Token {settings.PROVIDER_API_KEY}',
                            'Content-Type': 'application/json'
                        }
                    )
                    if response.status_code != 200:
                        self.message_user(
                            request, 
                            f'Provider 업체 승인 실패: {company.company_name}', 
                            level='ERROR'
                        )
                        continue
                except requests.RequestException as e:
                    self.message_user(
                        request, 
                        f'Provider 서버 통신 오류: {str(e)}', 
                        level='ERROR'
                    )
                    continue

            # 로컬 DB 업데이트
            company.status = 'approved'
            company.approved_by = request.user
            company.approved_at = timezone.now()
            company.save()

        self.message_user(request, f'{queryset.count()}개 업체가 승인되었습니다.')
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

    def sync_provider_companies(self, request, queryset):
        """Provider 서버의 업체 정보 동기화"""
        try:
            response = requests.get(
                f"{settings.PROVIDER_API_URL}/api/companies/pending/",
                headers={
                    'Authorization': f'Token {settings.PROVIDER_API_KEY}',
                    'Content-Type': 'application/json'
                }
            )
            
            if response.status_code == 200:
                synced_count = 0
                for company_data in response.json():
                    Company.objects.get_or_create(
                        business_registration_number=company_data['business_registration_number'],
                        defaults={
                            'company_name': company_data['company_name'],
                            'user_type': company_data['user_type'],
                            'email': company_data['email'],
                            'business_phone_number': company_data['business_phone_number'],
                            'status': 'pending',
                            'created_at': timezone.now()
                        }
                    )
                    synced_count += 1
                
                self.message_user(request, f'{synced_count}개 업체 정보가 동기화되었습니다.')
            else:
                self.message_user(request, 'Provider 서버 동기화 실패', level='ERROR')
                
        except requests.RequestException as e:
            self.message_user(request, f'동기화 중 오류 발생: {str(e)}', level='ERROR')
            
    sync_provider_companies.short_description = 'Provider 서버 동기화'

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
