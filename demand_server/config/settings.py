from pathlib import Path
from decouple import config
import os
import sys


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = True

PORT = config('PORT', default='8000')
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# API URL 설정
PROVIDER_API_URL = config('PROVIDER_API_URL', default='http://localhost:8001')
PROVIDER_API_KEY = config('PROVIDER_API_KEY')

if not PROVIDER_API_KEY:
    raise ValueError('PROVIDER_API_KEY must be set in .env file')

# CORS 설정
CORS_ALLOWED_ORIGINS = [
    # "http://localhost:8000",  # Demand Server
    "http://localhost:8001",  # Provider Server
    # "http://localhost:8002",  # Admin Panel
]

CORS_ALLOW_CREDENTIALS = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # REST framework
    'rest_framework',
    'rest_framework.authtoken',

    # 기본앱
    'api.apps.ApiConfig',
    'users.apps.UsersConfig',

    # social login
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'corsheaders',
]

AUTH_USER_MODEL = 'users.CustomUser'

SITE_ID = 1

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 반드시 CommonMiddleware 앞에 위치
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', 
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
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

# 토큰 인증 설정
TOKEN_EXPIRED_AFTER_SECONDS = 86400  # 24시간
