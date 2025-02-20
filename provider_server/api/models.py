from django.db import models
from django.conf import settings
from rest_framework.authtoken.models import Token

class APIToken(models.Model):
    """관리자 패널용 API 토큰"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_token',
        verbose_name='사용자'
    )
    token = models.OneToOneField(
        Token,
        on_delete=models.CASCADE,
        related_name='api_token',
        verbose_name='토큰'
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

    class Meta:
        verbose_name = 'API 토큰'
        verbose_name_plural = 'API 토큰 목록'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}의 API 토큰"

    def save(self, *args, **kwargs):
        if not self.token:
            # 토큰이 없는 경우 자동 생성
            token, _ = Token.objects.get_or_create(user=self.user)
            self.token = token
        super().save(*args, **kwargs)
