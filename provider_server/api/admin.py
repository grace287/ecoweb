from django.contrib import admin
from django.contrib import messages
from rest_framework.authtoken.models import Token
from django.urls import path
from django.shortcuts import redirect
from django.utils import timezone
from .models import APIToken

@admin.register(APIToken)
class AdminPanelTokenAdmin(admin.ModelAdmin):
    """관리자 패널용 API 토큰 관리"""
    list_display = ('token_key', 'user', 'created_at', 'is_active', 'last_used_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('token', 'created_at', 'last_used_at')

    def token_key(self, obj):
        return obj.token.key if obj.token else '-'
    token_key.short_description = '관리자 패널 토큰'

    def generate_token(self, request):
        """관리자 패널용 API 토큰 생성"""
        if not request.user.is_superuser:
            messages.error(request, '슈퍼유저만 토큰을 생성할 수 있습니다.')
            return redirect('admin:api_apipaneltoken_changelist')

        # 기존 토큰 비활성화
        APIToken.objects.filter(user=request.user).update(is_active=False)
        
        # 새 토큰 생성
        token = APIToken.objects.create(
            user=request.user,
            description=f'관리자 패널 인증용 ({request.user.username})'
        )
        
        messages.success(
            request, 
            f'새로운 관리자 패널 토큰이 생성되었습니다: {token.token.key}'
        )
        return redirect('admin:api_apipaneltoken_changelist')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'generate-token/', 
                self.admin_site.admin_view(self.generate_token),
                name='generate_admin_panel_token'
            ),
        ]
        return custom_urls + urls


@admin.register(Token)
class ServiceTokenAdmin(admin.ModelAdmin):
    """서비스 API 토큰 관리"""
    list_display = ('key', 'user', 'created', 'get_purpose')
    fields = ('user', 'key', 'created')
    readonly_fields = ('key', 'created')

    def get_purpose(self, obj):
        return '서비스 API용'
    get_purpose.short_description = '용도'
