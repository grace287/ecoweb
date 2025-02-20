from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class AdminUserManager(BaseUserManager):
    """관리자 계정 생성을 위한 매니저"""
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('아이디는 필수 입력 항목입니다.')
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        return self.create_user(username, password, **extra_fields)

class AdminUser(AbstractUser):
    """관리자 사용자 모델"""
    email = models.EmailField(unique=True, verbose_name='이메일')
    phone_number = models.CharField(max_length=20, verbose_name='연락처')
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='최근 로그인 IP')
    login_count = models.PositiveIntegerField(default=0, verbose_name='로그인 횟수')
    
    objects = AdminUserManager()

    class Meta:
        verbose_name = '관리자'
        verbose_name_plural = '관리자'

    def __str__(self):
        return f"관리자 - {self.username}"

    def save(self, *args, **kwargs):
        # 관리자 권한 자동 부여
        self.is_staff = True
        self.is_superuser = True
        super().save(*args, **kwargs)

    def log_login(self, ip_address):
        """로그인 정보 기록"""
        self.last_login_ip = ip_address
        self.login_count += 1
        self.save(update_fields=['last_login_ip', 'login_count', 'last_login'])

    def get_pending_companies(self):
        """승인 대기 중인 업체 조회"""
        return Company.objects.filter(status='pending')

    def get_company_stats(self):
        """업체 현황 통계"""
        return {
            'total': Company.objects.count(),
            'providers': Company.objects.filter(user_type='provider').count(),
            'demands': Company.objects.filter(user_type='demand').count(),
            'pending': Company.objects.filter(status='pending').count(),
            'approved': Company.objects.filter(status='approved').count(),
            'rejected': Company.objects.filter(status='rejected').count(),
        }

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
    
    # 기본 정보
    username = models.CharField(max_length=150, unique=True, verbose_name='아이디')
    email = models.EmailField(unique=True, verbose_name='이메일')
    company_name = models.CharField(max_length=255, verbose_name='업체명')
    business_registration_number = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name='사업자등록번호'
    )
    
    # 연락처 정보
    business_phone_number = models.CharField(max_length=20, verbose_name='대표번호')
    consultation_phone_number = models.CharField(
        max_length=20, 
        null=True, 
        blank=True, 
        verbose_name='상담번호'
    )
    
    # 주소 정보
    address = models.CharField(max_length=255, verbose_name='주소')
    address_detail = models.CharField(
        max_length=255, 
        null=True, 
        blank=True, 
        verbose_name='상세주소'
    )
    
    # 상태 정보
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES, 
        verbose_name='업체유형'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='승인상태'
    )
    
    # 승인 관련 정보
    approved_by = models.ForeignKey(
        AdminUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='승인처리자'
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='승인처리일')
    rejection_reason = models.TextField(null=True, blank=True, verbose_name='거부사유')
    
    # 시스템 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '회원업체'
        verbose_name_plural = '회원업체 목록'
        
    def __str__(self):
        return f"[{self.get_user_type_display()}] {self.company_name}"

    def verify_documents(self):
        """업체 제출 서류 검증"""
        required_docs = ['business', 'account']
        submitted_docs = self.companydocument_set.values_list('document_type', flat=True)
        return all(doc_type in submitted_docs for doc_type in required_docs)

    def get_missing_documents(self):
        """미제출 서류 확인"""
        required_docs = ['business', 'account']
        submitted_docs = self.companydocument_set.values_list('document_type', flat=True)
        return [doc for doc in required_docs if doc not in submitted_docs]

class CompanyDocument(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='업체')
    document_type = models.CharField(
        max_length=20,
        choices=[
            ('business', '사업자등록증'),
            ('account', '통장사본'),
            ('other', '기타')
        ],
        verbose_name='서류종류'
    )
    file = models.FileField(upload_to='company_docs/%Y/%m/', verbose_name='파일')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='업로드일시')

    class Meta:
        verbose_name = '업체서류'
        verbose_name_plural = '업체서류 목록'