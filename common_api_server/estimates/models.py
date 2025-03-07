from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import Q, F
from services.models import ServiceCategory

# 측정 장소 모델
class MeasurementLocation(models.Model):
    """측정 장소 모델"""
    name = models.CharField(max_length=50, unique=True, verbose_name="측정 장소")

    def __str__(self):
        return self.name

def get_default_service_category():
    category = ServiceCategory.objects.first()  # ✅ 첫 번째 카테고리 가져오기
    return category.id if category else None  # ✅ 존재하면 id 반환, 없으면 None

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

    SCHEDULE_CHOICES = [
        ('asap', '최대한 빨리'),
        ('3days', '3일 이내'),
        ('1week', '1주일 이내'),
        ('1month', '한 달 이내')
    ]


    @classmethod
    def get_estimates(cls, provider_user_id=None, demand_user_id=None, status=None):
        """필터링된 견적 목록 조회"""
        filters = Q()

        if provider_user_id:
            filters &= Q(provider_user_id=provider_user_id)
        if demand_user_id:
            filters &= Q(demand_user_id=demand_user_id)
        if status:
            filters &= Q(status=status)

        return cls.objects.filter(filters).order_by("-created_at")
    
    estimate_number = models.CharField(max_length=20, unique=True, verbose_name="견적번호")
    

    demand_user_id = models.IntegerField(null=True, blank=True)
    contact_name = models.CharField(max_length=100, null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    provider_user_id = models.IntegerField(null=True, blank=True, verbose_name="대행사 사용자 ID")  # Provider 서버 User ID

    # 기본 카테고리 필드 유지
    service_category = models.ForeignKey(
        ServiceCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='primary_estimates'
    )
    
    # 다대다 관계로 여러 카테고리 지원
    service_categories = models.ManyToManyField(
        ServiceCategory, 
        related_name='estimates'
    )
    
    measurement_locations = models.ManyToManyField(
        MeasurementLocation, related_name="estimates", verbose_name="측정 장소"
        )
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

    # 주소 필드 추가
    address = models.CharField(
        max_length=255, 
        verbose_name="측정 주소", 
        null=True,  # 기존 데이터와의 호환성을 위해 null 허용
        blank=True  # 관리자 페이지에서 빈 값 허용
    )

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
        
        # 금액 자동 계산 (None 값 방지)
        self.base_amount = self.base_amount or 0
        self.discount_amount = self.discount_amount or 0
        self.vat_amount = self.base_amount * 0.1
        self.total_amount = self.base_amount + self.vat_amount - self.discount_amount
        
        super().save(*args, **kwargs)

    def generate_estimate_number(self):
        """견적 번호 생성 (중복 방지)"""
        prefix = timezone.now().strftime('%Y%m%d')
        
        # 원자적 증가를 위해 F() 활용
        last_number = (
            Estimate.objects.filter(estimate_number__startswith=prefix)
            .annotate(last_num=F('estimate_number'))
            .order_by('-estimate_number')
            .values_list('last_num', flat=True)
            .first()
        )

        if last_number:
            new_number = str(int(last_number[-4:]) + 1).zfill(4)
        else:
            new_number = '0001'

        return f"{prefix}{new_number}"


# 측정 항목 모델
class MeasurementItem(models.Model):
    """측정 항목 모델"""
    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE, related_name="measurement_items", verbose_name="견적")
    category = models.ForeignKey("services.ServiceCategory", on_delete=models.CASCADE, verbose_name="측정 종류")
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


# 견적 첨부파일 모델
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

    class Meta:
        verbose_name = "견적 첨부파일"
        verbose_name_plural = "견적 첨부파일 목록"

    def __str__(self):
        return f"{self.estimate.estimate_number} - {self.file_type}"