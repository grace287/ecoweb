from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator


# 서비스 카테고리 모델
class ServiceCategory(models.Model):
    """공통 서비스 카테고리 모델"""
    CATEGORY_CHOICES = [
        ('indoor-air', '실내공기질'),
        ('noise-vibration', '소음·진동'),
        ('odor', '악취'),
        ('water', '수질'),
        ('air', '대기'),
        ('major-disaster', '중대재해'),
        ('office', '사무실'),
        ('esg', 'ESG경영'),
        ('etc', '기타'),
    ]
    category_code = models.CharField(max_length=50, unique=True, verbose_name="카테고리 코드")
    name = models.CharField(max_length=255, unique=True, verbose_name="서비스 카테고리명")
    description = models.TextField(null=True, blank=True, verbose_name="설명")

    class Meta:
        verbose_name = "측정 종류"
        verbose_name_plural = "서비스 카테고리 목록"

    def __str__(self):
        return self.name


# 측정 장소 모델
class MeasurementLocation(models.Model):
    """측정 장소 모델"""
    name = models.CharField(max_length=50, unique=True, verbose_name="측정 장소")

    def __str__(self):
        return self.name


# 견적서 모델
class Estimate(models.Model):
    """견적서 모델"""
    STATUS_CHOICES = [
        ('REQUEST', '견적요청'),
        ('WORKING', '작성중'),
        ('RESPONSE', '견적응답'),
        ('APPROVED', '수락'),
        ('REJECTED', '거절'),
        ('PAID', '결제완료'),
        ('CANCELLED', '취소')
    ]

    demand_user_id = models.IntegerField(verbose_name="수요업체 사용자 ID")  # Demand 서버 User ID
    provider_user_id = models.IntegerField(null=True, blank=True, verbose_name="대행사 사용자 ID")  # Provider 서버 User ID

    
    service_category = models.ManyToManyField(ServiceCategory, related_name="estimates", verbose_name="서비스 카테고리")
    estimate_number = models.CharField(max_length=20, unique=True, verbose_name="견적번호")
    
    measurement_locations = models.ManyToManyField(MeasurementLocation, related_name="estimates", verbose_name="측정 장소")
    preferred_schedule = models.CharField(
        max_length=20,
        choices=[
            ('asap', '최대한 빨리'),
            ('within_3_days', '3일 이내'),
            ('within_1_week', '1주일 이내'),
            ('within_1_month', '한 달 이내'),
        ],
        verbose_name="희망 일정"
    )

    # 연락처 및 사업자 정보
    contact_name = models.CharField(max_length=100, verbose_name="담당자명")
    contact_phone = models.CharField(max_length=20, verbose_name="연락처")
    contact_email = models.EmailField(verbose_name="이메일")
    business_registration_number = models.CharField(max_length=20, unique=True, verbose_name="사업자등록번호", null=True, blank=True)

    # 금액 정보
    base_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, validators=[MinValueValidator(0)], verbose_name="기본 금액")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="할인 금액")
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, validators=[MinValueValidator(0)], verbose_name="부가세")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, validators=[MinValueValidator(0)], verbose_name="최종 금액")

    # 상태 및 일자
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='REQUEST', verbose_name="상태")
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name="유효기간")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        db_table = 'estimates'
        ordering = ['-created_at']
        verbose_name = "견적서"
        verbose_name_plural = "견적서 목록"

    def __str__(self):
        return f"견적서 #{self.estimate_number}"

    def save(self, *args, **kwargs):
        if not self.estimate_number:
            self.estimate_number = self.generate_estimate_number()
        
        # 금액 자동 계산
        if self.base_amount:
            self.vat_amount = self.base_amount * 0.1
            self.total_amount = self.base_amount + self.vat_amount - self.discount_amount
            
        super().save(*args, **kwargs)

    def generate_estimate_number(self):
        prefix = timezone.now().strftime('%Y%m%d')
        last_estimate = Estimate.objects.filter(estimate_number__startswith=prefix).order_by('-estimate_number').first()
        
        if last_estimate:
            last_number = int(last_estimate.estimate_number[-4:])
            new_number = str(last_number + 1).zfill(4)
        else:
            new_number = '0001'
            
        return f"{prefix}{new_number}"


# 측정 항목 모델
class MeasurementItem(models.Model):
    """측정 항목 모델"""
    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE, related_name="measurement_items", verbose_name="견적")
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, verbose_name="측정 종류")  # 기존 CharField → ForeignKey
    unit_price = models.PositiveIntegerField(verbose_name="단가")
    maintain_quantity = models.PositiveIntegerField(verbose_name="유지 개수")
    recommend_quantity = models.PositiveIntegerField(verbose_name="권고 개수")
    subtotal = models.PositiveIntegerField(verbose_name="합계", editable=False)  # 자동 계산 필드

    class Meta:
        verbose_name = "측정 항목"
        verbose_name_plural = "측정 항목 목록"

    def __str__(self):
        return f"{self.category.name} - {self.estimate.estimate_number}"

    def save(self, *args, **kwargs):
        """Subtotal 자동 계산"""
        self.subtotal = (self.maintain_quantity + self.recommend_quantity) * self.unit_price
        super().save(*args, **kwargs)



class EstimateAttachment(models.Model):
    """견적 첨부파일 모델"""
    FILE_TYPE_CHOICES = [
        ('business', '사업자등록증'),
        ('site', '현장 사진'),
        ('other', '기타')
    ]

    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE, related_name="attachments", verbose_name="견적")
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, verbose_name="파일 유형")
    file = models.FileField(upload_to="estimate_attachments/%Y/%m/%d/", verbose_name="파일")  # 날짜별 저장 경로 개선

    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="업로드일")