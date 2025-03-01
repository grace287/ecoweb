from django.db import models
from enum import Enum

class ServiceCategoryEnum(Enum):
    INDOOR_AIR = ("indoor-air", "실내공기질")
    NOISE_VIBRATION = ("noise-vibration", "소음·진동")
    ODOR = ("odor", "악취")
    WATER = ("water", "수질")
    AIR = ("air", "대기")
    MAJOR_DISASTER = ("major-disaster", "중대재해")
    OFFICE = ("office", "사무실")
    ESG = ("esg", "ESG경영")
    ETC = ("etc", "기타")

    @classmethod
    def choices(cls):
        return [(item.value[0], item.value[1]) for item in cls]

class ServiceCategory(models.Model):
    """공통 서비스 카테고리 모델"""
    category_code = models.CharField(
        max_length=50, 
        unique=True, 
        choices=ServiceCategoryEnum.choices(),  # ✅ ENUM에서 선택 옵션 가져오기
        verbose_name="카테고리 코드"
    )
    name = models.CharField(max_length=255, unique=True, verbose_name="서비스 카테고리명")
    description = models.TextField(null=True, blank=True, verbose_name="설명")

    class Meta:
        verbose_name = "측정 종류"
        verbose_name_plural = "서비스 카테고리 목록"

    def __str__(self):
        return self.name