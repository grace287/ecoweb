from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from .managers import ProviderUserManager  # ✅ ProviderUserManager 추가
import requests
from django.conf import settings

class ProviderUser(AbstractUser):
    """대행사 사용자 모델 (Provider 서버)"""
    objects = ProviderUserManager()  # ✅ UserManager 추가

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

    company_name = models.CharField(max_length=255, verbose_name="업체명")
    business_registration_number = models.CharField(max_length=20, unique=True, verbose_name="사업자등록번호")
    business_phone_number = models.CharField(max_length=20, verbose_name="대표번호")
    consultation_phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="상담번호")
    address = models.CharField(max_length=255, verbose_name="주소")
    address_detail = models.CharField(max_length=255, null=True, blank=True, verbose_name="상세 주소")

    # ✅ ProviderUser는 공통 API 서버의 ServiceCategory를 참조 가능
    service_category = models.ManyToManyField(
        "ServiceCategory",
        related_name="providers",
        verbose_name="서비스 분야"
    )

    is_approved = models.BooleanField(default=False, verbose_name="승인 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        db_table = "provider_users"
        verbose_name = "대행사 사용자"
        verbose_name_plural = "대행사 사용자 목록"

    def __str__(self):
        return f"{self.company_name} ({self.username})"
class ServiceCategory(models.Model):
    """공통 API 서버의 ServiceCategory 데이터를 동기화하는 모델"""
    category_code = models.CharField(max_length=20, unique=True, verbose_name="카테고리 코드")
    name = models.CharField(max_length=255, verbose_name="분야")

    class Meta:
        verbose_name = "서비스 카테고리"
        verbose_name_plural = "서비스 카테고리 목록"

    def __str__(self):
        return self.name

    @staticmethod
    def sync_service_categories():
        """공통 API 서버에서 `ServiceCategory` 데이터를 동기화하는 메서드"""
        try:
            response = requests.get(f"{settings.COMMON_API_URL}/service-categories/")
            if response.status_code == 200:
                categories = response.json()
                for category in categories:
                    ServiceCategory.objects.update_or_create(
                        category_code=category["category_code"],
                        defaults={"name": category["name"]}
                    )
        except Exception as e:
            print(f"⚠️ 서비스 카테고리 동기화 오류: {e}")




class Attachment(models.Model):
    """회원가입 시 제출하는 첨부파일 모델"""
    FILE_TYPE_CHOICES = [
        ("business", "사업자등록증"),
        ("other", "기타"),
    ]

    user = models.ForeignKey(
        ProviderUser,  # ✅
        related_name="attachments",
        on_delete=models.CASCADE,
        verbose_name="사용자"
    )
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, verbose_name="파일 유형")
    file = models.FileField(upload_to="attachments/", verbose_name="첨부파일")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="업로드일")

    class Meta:
        verbose_name = "첨부파일"
        verbose_name_plural = "첨부파일 목록"

    def __str__(self):
        return f"{self.user.company_name} - {self.file_type}"


