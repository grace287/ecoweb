from pathlib import Path
from decouple import config
import os
import sys


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)  # ✅ 운영 환경에서는 False 유지


PORT = config('PORT', default='8000')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')


# API URL 설정
DEMAND_API_URL = config('DEMAND_API_URL', default='http://localhost:8000')
PROVIDER_API_URL = config('PROVIDER_API_URL', default='http://localhost:8001')
ADMIN_PANEL_URL = config('ADMIN_PANEL_URL', default='http://localhost:8002')
COMMON_API_URL = config('COMMON_API_URL', default='http://localhost:8003') 
PAYMENT_API_URL = config('PAYMENT_API_URL', default='http://localhost:8004')

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",  # demand_server
    "http://localhost:8000",
]

CORS_ALLOW_CREDENTIALS = True  # credentials: 'include' 허용

# 필요한 경우 추가 CORS 설정
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # REST framework
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',

    # 기본앱
    'api.apps.ApiConfig',
    'users',

    'corsheaders',

    # social login
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.naver',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.kakao',
]

AUTH_USER_MODEL = "users.DemandUser"


SITE_ID = 1
# 아이디 또는 이메일로 로그인 가능
ACCOUNT_LOGIN_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 반드시 CommonMiddleware보다 앞에 위치
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', 
]
# 모든 도메인 허용 (보안상 위험할 수 있음)
CORS_ALLOW_ALL_ORIGINS = True  

# CORS 설정
# CORS_ALLOWED_ORIGINS = [
#     "http://127.0.0.1:8000",
#     "http://localhost:8000",
#     "http://localhost:8001",
#     "http://localhost:8002",
#     "http://localhost:8003",
#     "http://localhost:8004",
# ]

CORS_ALLOW_CREDENTIALS = True  # 인증 정보 포함 요청 허용
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = ["*"]
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # 기본 인증 백엔드
    'allauth.account.auth_backends.AuthenticationBackend',  # 소셜 로그인 백엔드
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 로그인/로그아웃 관련 설정
LOGIN_REDIRECT_URL = 'main'  # 로그인 후 리다이렉트할 URL
LOGOUT_REDIRECT_URL = 'main'  # 로그아웃 후 리다이렉트할 URL
LOGIN_URL = 'login'  # 로그인 URL



# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/
# 시간대 설정
TIME_ZONE = 'Asia/Seoul'
USE_TZ = True
USE_I18N = True
USE_L10N = True

# 언어 설정
LANGUAGE_CODE = 'ko-kr'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 세션이 유지되도록 설정 (자동 로그아웃 방지)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7일
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# REST Framework 설정
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.AllowAny',
    ],
}


# 토큰 인증 설정
TOKEN_EXPIRED_AFTER_SECONDS = 86400  # 24시간

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}