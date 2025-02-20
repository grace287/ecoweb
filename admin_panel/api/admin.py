from django.contrib import admin
from django.contrib import messages
from django.utils import timezone
from .models import AdminPanelToken

@admin.register(AdminPanelToken)
class AdminPanelTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_display', 'created_at', 'expires_at', 'is_active', 'status')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('token', 'created_at', 'last_used_at')
    
    def token_display(self, obj):
        """토큰 일부만 표시 (보안)"""
        if obj.token:
            return f"{obj.token[:10]}...{obj.token[-5:]}"
        return "-"
    token_display.short_description = "토큰"

    def status(self, obj):
        """토큰 상태 표시"""
        if not obj.is_active:
            return '비활성'
        if obj.is_expired():
            return '만료됨'
        return '활성'
    status.short_description = "상태"

    def save_model(self, request, obj, form, change):
        """토큰 저장 시 환경 변수에도 자동 반영"""
        if not change:  # 새로운 토큰 생성 시
            from django.utils.crypto import get_random_string
            obj.token = get_random_string(length=40)
            
            # 기존 활성 토큰들 비활성화
            AdminPanelToken.objects.filter(
                user=obj.user,
                is_active=True
            ).update(is_active=False)

        super().save_model(request, obj, form, change)
        
        if obj.is_active and not obj.is_expired():
            self.update_env_file(obj.token)
            messages.success(
                request, 
                f'관리자 토큰이 생성되었습니다. 토큰: {obj.token}\n'
                '이 토큰은 다시 표시되지 않으니 안전한 곳에 보관하세요.'
            )

    def update_env_file(self, token):
        """토큰을 .env 파일에 저장"""
        import os
        from pathlib import Path

        env_path = Path(__file__).resolve().parent.parent.parent / '.env'
        
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # ADMIN_TOKEN 라인 찾아서 수정
            found = False
            for i, line in enumerate(lines):
                if line.startswith('ADMIN_TOKEN='):
                    lines[i] = f'ADMIN_TOKEN={token}\n'
                    found = True
                    break

            # 없으면 추가
            if not found:
                lines.append(f'ADMIN_TOKEN={token}\n')

            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

    def has_delete_permission(self, request, obj=None):
        """삭제 권한 제한"""
        return request.user.is_superuser

    def get_readonly_fields(self, request, obj=None):
        """수정 시 읽기 전용 필드 설정"""
        if obj:  # 수정 시
            return self.readonly_fields + ('user',)
        return self.readonly_fields
