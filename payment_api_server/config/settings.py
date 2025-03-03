from pathlib import Path
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')
SECRET_KEY = 'django-insecure-9%w$_1vu2z58gq@ogn@+kk2)xf_sc0=3nl+gp@1*qd#ptpp^z@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

PORT = config('PORT', default='8004')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

DEMAND_API_URL = config('DEMAND_API_URL', default='http://localhost:8000')
PROVIDER_API_URL = config('PROVIDER_API_URL', default='http://localhost:8001')
ADMIN_PANEL_URL = config('ADMIN_PANEL_URL', default='http://localhost:8002')
COMMON_API_URL = config('COMMON_API_URL', default='http://localhost:8003') 
PAYMENT_API_URL = config('PAYMENT_API_URL', default='http://localhost:8004')


# PG사 설정
TOSS_PAYMENTS_API_KEY = config('TOSS_PAYMENTS_API_KEY')
TOSS_PAYMENTS_API_SECRET = config('TOSS_PAYMENTS_API_SECRET')
SITE_URL = config('SITE_URL', default='http://localhost:8004')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'payment',

    # Third party apps
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# PG사 설정
TOSS_PAYMENTS_API_KEY = 'your-api-key'
TOSS_PAYMENTS_API_SECRET = 'your-api-secret'
SITE_URL = 'https://your-domain.com'

# 결제 수단 설정
PAYMENT_METHODS = {
    'CARD': {
        'code': 'card',
        'name': '신용·체크카드',
        'enabled': True
    },
    'KAKAO': {
        'code': 'kakao',
        'name': '카카오페이',
        'enabled': True
    },
    'NAVER': {
        'code': 'naver',
        'name': '네이버페이',
        'enabled': True
    },
    'TOSS': {
        'code': 'tosspay',
        'name': '토스페이',
        'enabled': True
    },
    'PAYCO': {
        'code': 'payco',
        'name': '페이코',
        'enabled': True
    }
}
