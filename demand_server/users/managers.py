from django.contrib.auth.models import BaseUserManager

class DemandUserManager(BaseUserManager):
    """DemandUser 모델을 위한 사용자 매니저"""
    
    def create_user(self, username, email, password=None, **extra_fields):
        """일반 사용자 생성"""
        if not username:
            raise ValueError("아이디(username)는 필수입니다.")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """슈퍼유저 생성"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)
