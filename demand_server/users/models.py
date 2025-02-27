from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from .managers import DemandUserManager

class DemandUser(AbstractUser):
    objects = DemandUserManager()
    
    groups = models.ManyToManyField(
        Group,
        related_name="demanduser_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="demanduser_permissions",
        blank=True
    )
    """수요업체 사용자 모델"""
    company_name = models.CharField(max_length=255, verbose_name="회사명", null=True, blank=True)
    business_phone_number = models.CharField(max_length=20, verbose_name="대표번호", null=True, blank=True)
    contact_phone_number = models.CharField(max_length=20, verbose_name="담당자 연락처", null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name="주소", null=True, blank=True)
    address_detail = models.CharField(max_length=255, verbose_name="상세 주소", null=True, blank=True)
    recommend_id = models.CharField(max_length=100, verbose_name="추천인 아이디", blank=True, null=True)
    
    is_approved = models.BooleanField(default=False, verbose_name="승인 여부")  # 가입 승인 여부
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        db_table = "demand_users"
        verbose_name = "수요업체 사용자"
        verbose_name_plural = "수요업체 사용자 목록"

    def __str__(self):
        return f"{self.company_name} ({self.username})"