from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
import uuid

class ProviderUserManager(BaseUserManager):
    """ProviderUser를 위한 매니저"""
    def create_user(self, username, email, password=None, **extra_fields):
        """일반 사용자 생성"""
        if not username:
            raise ValueError(_('The Username must be set'))

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        
        # 사업자등록번호가 없는 경우 고유한 값 생성
        if not extra_fields.get('business_registration_number'):
            # UUID를 사용하여 고유한 값 생성
            extra_fields['business_registration_number'] = f'SUPERUSER_{uuid.uuid4().hex[:10]}'
        
        # 모든 필수 필드에 기본값 설정
        extra_fields.setdefault('company_name', username)
        extra_fields.setdefault('business_phone_number', '000-000-0000')
        extra_fields.setdefault('address', '미지정')
        
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """슈퍼유저 생성"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(username, email, password, **extra_fields)
