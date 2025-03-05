from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.utils import timezone
import requests
from django.conf import settings

class AdminUserManager(BaseUserManager):
    """관리자 계정 생성을 위한 매니저"""
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('아이디는 필수 입력 항목입니다.')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class AdminUser(AbstractUser):
    """관리자 사용자 모델"""
    email = models.EmailField(unique=True, verbose_name='이메일')
    phone_number = models.CharField(max_length=20, verbose_name='연락처', null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='최근 로그인 IP')
    login_count = models.PositiveIntegerField(default=0, verbose_name='로그인 횟수')
    
    objects = AdminUserManager()

    groups = models.ManyToManyField(
        Group,
        related_name="adminuser_groups",
        blank=True,
        verbose_name='그룹'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="adminuser_permissions",
        blank=True,
        verbose_name='사용자 권한'
    )

    class Meta:
        verbose_name = '관리자'
        verbose_name_plural = '관리자 목록'

    def __str__(self):
        return f"관리자 - {self.username}"

    def log_login(self, ip_address):
        """로그인 정보 기록"""
        self.last_login_ip = ip_address
        self.login_count += 1
        self.save(update_fields=['last_login_ip', 'login_count', 'last_login'])

class DemandUser(AbstractUser):
    """수요업체 사용자 모델"""
    company_name = models.CharField(max_length=255, verbose_name="회사명", null=True, blank=True)
    business_phone_number = models.CharField(max_length=20, verbose_name="대표번호", null=True, blank=True)
    contact_phone_number = models.CharField(max_length=20, verbose_name="담당자 연락처", null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name="주소", null=True, blank=True)
    address_detail = models.CharField(max_length=255, verbose_name="상세 주소", null=True, blank=True)
    recommend_id = models.CharField(max_length=100, verbose_name="추천인 아이디", blank=True, null=True)
    
    is_approved = models.BooleanField(default=False, verbose_name="승인 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    groups = models.ManyToManyField(
        Group,
        related_name="demanduser_groups",
        blank=True,
        verbose_name='그룹'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="demanduser_permissions",
        blank=True,
        verbose_name='사용자 권한'
    )

    class Meta:
        verbose_name = '수요업체 사용자'
        verbose_name_plural = '수요업체 사용자 목록'

    def __str__(self):
        return f"{self.company_name} ({self.username})"

class ProviderUser(AbstractUser):
    """대행사 사용자 모델"""
    company_name = models.CharField(max_length=255, verbose_name="업체명")
    business_registration_number = models.CharField(max_length=20, unique=True, verbose_name="사업자등록번호")
    business_phone_number = models.CharField(max_length=20, verbose_name="대표번호")
    consultation_phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="상담번호")
    address = models.CharField(max_length=255, verbose_name="주소")
    address_detail = models.CharField(max_length=255, null=True, blank=True, verbose_name="상세 주소")

    is_approved = models.BooleanField(default=False, verbose_name="승인 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    groups = models.ManyToManyField(
        Group,
        related_name="provideruser_groups",
        blank=True,
        verbose_name='그룹'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="provideruser_permissions",
        blank=True,
        verbose_name='사용자 권한'
    )

    class Meta:
        verbose_name = '대행사 사용자'
        verbose_name_plural = '대행사 사용자 목록'

    def __str__(self):
        return f"{self.company_name} ({self.username})"

class ServiceCategory(models.Model):
    """서비스 카테고리 모델"""
    category_code = models.CharField(max_length=20, unique=True, verbose_name="카테고리 코드")
    name = models.CharField(max_length=255, verbose_name="분야")
    description = models.TextField(null=True, blank=True, verbose_name="설명")

    class Meta:
        verbose_name = "서비스 카테고리"
        verbose_name_plural = "서비스 카테고리 목록"

    def __str__(self):
        return self.name

    @classmethod
    def sync_service_categories(cls):
        """공통 API 서버에서 서비스 카테고리 동기화"""
        try:
            response = requests.get(f"{settings.COMMON_API_URL}/service-categories/")
            
            if response.status_code == 200:
                categories = response.json()
                for category in categories:
                    cls.objects.update_or_create(
                        category_code=category["category_code"],
                        defaults={
                            "name": category["name"],
                            "description": category.get("description", "")
                        }
                    )
                return True
            return False
        except Exception as e:
            print(f"서비스 카테고리 동기화 오류: {e}")
            return False

class Company(models.Model):
    """업체 정보 모델"""
    USER_TYPE_CHOICES = [
        ('provider', '대행사'),
        ('demand', '수요업체'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '승인대기'),
        ('approved', '승인완료'),
        ('rejected', '승인거부'),
    ]

    demand_user = models.OneToOneField(
        DemandUser, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='company',
        verbose_name='수요업체 사용자'
    )
    provider_user = models.OneToOneField(
        ProviderUser, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='company',
        verbose_name='대행사 사용자'
    )
    
    username = models.CharField(max_length=150, unique=True, verbose_name='아이디')
    email = models.EmailField(unique=True, verbose_name='이메일')
    company_name = models.CharField(max_length=255, verbose_name='업체명')
    business_registration_number = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name='사업자등록번호'
    )
    
    business_phone_number = models.CharField(max_length=20, verbose_name='대표번호')
    consultation_phone_number = models.CharField(
        max_length=20, 
        null=True, 
        blank=True, 
        verbose_name='상담번호'
    )
    
    address = models.CharField(max_length=255, verbose_name='주소')
    address_detail = models.CharField(
        max_length=255, 
        null=True, 
        blank=True, 
        verbose_name='상세주소'
    )
    
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES, 
        verbose_name='업체유형'
    )
    status = models.CharField(max_length=20, choices=[('pending', '승인대기'), ('approved', '승인완료')])

    
    approved_by = models.ForeignKey(
        AdminUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='승인처리자'
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='승인처리일')
    rejection_reason = models.TextField(null=True, blank=True, verbose_name='거부사유')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '회원업체'
        verbose_name_plural = '회원업체 목록'
        
    def __str__(self):
        return f"[{self.get_user_type_display()}] {self.company_name}"

class CompanyDocument(models.Model):
    """업체 제출 서류 모델"""
    DOCUMENT_TYPE_CHOICES = [
        ('business', '사업자등록증'),
        ('account', '통장사본'),
        ('other', '기타')
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='업체')
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name='서류종류'
    )
    file = models.FileField(upload_to='company_docs/%Y/%m/', verbose_name='파일')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='업로드일시')

    class Meta:
        verbose_name = '업체서류'
        verbose_name_plural = '업체서류 목록'

    def __str__(self):
        return f"{self.company.company_name} - {self.get_document_type_display()}"