from pathlib import Path
from decouple import config
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = config('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

PORT = config('PORT', default='8003')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps
    'authentication',
    'api',
    'services',
    'estimates',
    

    # Third party apps
    'rest_framework',
    'rest_framework.authtoken',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.naver',
    'allauth.socialaccount.providers.kakao',
]

DEMAND_SERVER_URL = "http://127.0.0.1:8000"  # Demand 서버 주소
PROVIDER_SERVER_URL = "http://127.0.0.1:8001"  # Provider 서버 주소


SITE_ID = 1  # django.contrib.sites에서 사용할 사이트 ID

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # 기본 인증 백엔드
    'allauth.account.auth_backends.AuthenticationBackend',  # allauth 백엔드
]
AUTH_USER_MODEL = 'authentication.User'

MIDDLEWARE = [
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
        'DIRS': [],
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


COMMON_API_URL = config('COMMON_API_URL', default='http://localhost:8003')


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

# 소셜 로그인 설정
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET')
GOOGLE_CALLBACK_URL = 'http://localhost:8003/auth/google/callback/'

KAKAO_CLIENT_ID = config('KAKAO_CLIENT_ID')
KAKAO_CLIENT_SECRET = config('KAKAO_CLIENT_SECRET')
KAKAO_CALLBACK_URL = 'http://localhost:8003/auth/kakao/callback/'

NAVER_CLIENT_ID = config('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = config('NAVER_CLIENT_SECRET')
NAVER_CALLBACK_URL = 'http://localhost:8003/auth/naver/callback/'

# JWT 설정
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID'),
            'secret': config('GOOGLE_CLIENT_SECRET'),
            'key': ''
        }
    },
    'naver': {
        'APP': {
            'client_id': config('NAVER_CLIENT_ID'),
            'secret': config('NAVER_CLIENT_SECRET'),
            'key': ''
        }
    },
    'kakao': {
        'APP': {
            'client_id': config('KAKAO_CLIENT_ID'),
            'secret': config('KAKAO_CLIENT_SECRET'),
            'key': ''
        }
    }
}