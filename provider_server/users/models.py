from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True, verbose_name="아이디")
    email = models.EmailField(unique=True, verbose_name="아이디(이메일)")
    company_name = models.CharField(max_length=255, verbose_name="업체명")
    business_registration_number = models.CharField(max_length=20, unique=True, verbose_name="사업자등록번호")
    business_phone_number = models.CharField(max_length=20, verbose_name="대표번호")
    consultation_phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="상담번호")
    address = models.CharField(max_length=255, verbose_name="주소")
    address_detail = models.CharField(max_length=255, null=True, blank=True, verbose_name="나머지 주소")
    service_category = models.ManyToManyField(
        ServiceCategory,
        related_name='providers',
        verbose_name='분야'
    )
    is_approved = models.BooleanField(default=False, verbose_name='승인 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

class Attachment(models.Model):
    user = models.ForeignKey(CustomUser, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/', verbose_name='첨부파일')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='업로드일')


class ProviderUser(AbstractUser):
    """대행사 사용자 모델 (Provider 서버)"""
    company_name = models.CharField(max_length=255, verbose_name="업체명")
    business_registration_number = models.CharField(max_length=20, unique=True, verbose_name="사업자등록번호")
    business_phone_number = models.CharField(max_length=20, verbose_name="대표번호")
    consultation_phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="상담번호")
    address = models.CharField(max_length=255, verbose_name="주소")
    address_detail = models.CharField(max_length=255, null=True, blank=True, verbose_name="상세 주소")

    # ✅ ProviderUser는 공통 API 서버의 ServiceCategory를 참조 가능
    service_category = models.ManyToManyField(
        ServiceCategory,
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