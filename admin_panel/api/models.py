from django.db import models
from django.conf import settings
class AdminPanelToken(models.Model):
    """관리자 패널 토큰 관리"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_tokens',
        verbose_name='관리자'
    )
    token = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='관리자 토큰'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일'
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='마지막 사용일'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='설명'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='활성화 상태'
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='만료일'
    )

    class Meta:
        verbose_name = '관리자 패널 토큰'
        verbose_name_plural = '관리자 패널 토큰 목록'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}의 관리자 토큰 ({self.created_at.strftime('%Y-%m-%d')})"

    def is_expired(self):
        """토큰 만료 여부 확인"""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False
