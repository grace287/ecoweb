from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Payment(models.Model):
    """결제 모델"""
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', '결제대기'),
        ('PROCESSING', '처리중'),
        ('COMPLETED', '결제완료'),
        ('FAILED', '결제실패'),
        ('CANCELLED', '결제취소'),
        ('REFUNDED', '환불완료')
    ]

    PAYMENT_METHOD_CHOICES = [
        ('kakao', '카카오페이'),
        ('naver', '네이버페이'),
        ('tosspay', '토스페이'),
        ('payco', '페이코'),
        ('card', '신용·체크카드'),
        ('bank_transfer', '계좌이체'),
        ('virtual_account', '가상계좌'),
        ('other', '기타')
    ]

    # 결제 기본 정보
    id = models.AutoField(primary_key=True, verbose_name="결제 식별자")
    estimate_id = models.IntegerField(
        verbose_name="견적 id",
        default=0
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="결제 금액"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="결제방법"
    )
    is_paid = models.BooleanField(
        default=False,
        verbose_name="결제 여부"
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="결제 완료 시간"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성 일자"
    )

    # 결제 금액 정보
    vat_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="부가세"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="총 결제금액"
    )

    # 결제 상태 및 방법
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING',
        verbose_name="결제상태"
    )

    # 결제 처리 정보
    pg_transaction_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="PG사 거래번호"
    )
    payment_key = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="결제 키"
    )

    # 시간 정보
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일시"
    )

    class Meta:
        db_table = 'payment'
        ordering = ['-created_at']
        verbose_name = "결제"
        verbose_name_plural = "결제 목록"

    def __str__(self):
        return f"Payment #{self.id} - {self.amount}"

    def complete_payment(self):
        """결제 완료 처리"""
        self.is_paid = True
        self.paid_at = timezone.now()
        self.status = 'COMPLETED'
        self.save()

    def save(self, *args, **kwargs):
        if not self.vat_amount:
            self.vat_amount = self.amount * 0.1
        
        self.total_amount = self.amount + self.vat_amount
        
        super().save(*args, **kwargs)


class PaymentRefund(models.Model):
    """결제 환불 모델"""
    REFUND_STATUS_CHOICES = [
        ('PENDING', '환불대기'),
        ('PROCESSING', '처리중'),
        ('COMPLETED', '환불완료'),
        ('FAILED', '환불실패')
    ]

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='refunds',
        verbose_name="결제"
    )
    refund_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="환불번호"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="환불금액"
    )
    reason = models.TextField(verbose_name="환불사유")
    status = models.CharField(
        max_length=20,
        choices=REFUND_STATUS_CHOICES,
        default='PENDING',
        verbose_name="환불상태"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="환불완료일시"
    )

    class Meta:
        db_table = 'payment_refunds'
        ordering = ['-created_at']
        verbose_name = "환불"
        verbose_name_plural = "환불 목록"

    def __str__(self):
        return f"환불 #{self.refund_number}"

    def save(self, *args, **kwargs):
        if not self.refund_number:
            self.refund_number = self.generate_refund_number()
        
        if self.status == 'COMPLETED' and not self.completed_at:
            self.completed_at = timezone.now()
            
        super().save(*args, **kwargs)

    def generate_refund_number(self):
        """환불 번호 생성"""
        prefix = timezone.now().strftime('%Y%m%d')
        last_refund = PaymentRefund.objects.filter(
            refund_number__startswith=prefix
        ).order_by('-refund_number').first()

        if last_refund:
            last_number = int(last_refund.refund_number[-4:])
            new_number = str(last_number + 1).zfill(4)
        else:
            new_number = '0001'

        return f"R{prefix}{new_number}"
