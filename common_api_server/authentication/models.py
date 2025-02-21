from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """소셜 로그인을 지원하는 사용자 모델"""
    PROVIDER_CHOICES = [
        ('local', '일반'),
        ('google', 'Google'),
        ('naver', 'Naver'),
        ('kakao', 'Kakao')
    ]

    # 기존 AbstractUser 필드 유지
    email = models.EmailField(_('email address'), blank=True)
    
    # 소셜 로그인 관련 필드
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        default='local',
        verbose_name='인증 제공자'
    )
    social_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        unique=True,
        verbose_name='소셜 아이디'
    )
    profile_image = models.URLField(
        null=True,
        blank=True,
        verbose_name='프로필 이미지'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='이메일 인증 여부'
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='마지막 로그인 IP'
    )

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자 목록'
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return f"{self.username} ({self.get_provider_display()})"

class SocialAccount(models.Model):
    """소셜 계정 연동 정보"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_accounts',
        verbose_name='사용자'
    )
    provider = models.CharField(
        max_length=20,
        choices=User.PROVIDER_CHOICES,
        verbose_name='제공자'
    )
    social_id = models.CharField(
        max_length=100,
        verbose_name='소셜 아이디'
    )
    extra_data = models.JSONField(
        default=dict,
        verbose_name='추가 정보'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일'
    )

    class Meta:
        verbose_name = '소셜 계정'
        verbose_name_plural = '소셜 계정 목록'
        unique_together = ('provider', 'social_id')
