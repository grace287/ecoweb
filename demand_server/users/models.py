from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    company_name = models.CharField(max_length=255, verbose_name="회사명")
    business_phone_number = models.CharField(max_length=20, verbose_name="담당자 휴대폰 번호")
    address = models.CharField(max_length=255, verbose_name="주소")
    address_detail = models.CharField(max_length=255, verbose_name="상세 주소", blank=True, null=True)
    recommend_id = models.CharField(max_length=100, verbose_name="추천인 아이디", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # related_name 설정
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # related_name 설정
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username