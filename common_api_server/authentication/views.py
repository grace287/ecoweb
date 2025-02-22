from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from users.models import CustomUser
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from . import models

User = get_user_model()

class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_CALLBACK_URL
    client_class = OAuth2Client

    def get_response(self):
        response = super().get_response()
        if self.user:
            self.user.provider = 'google'
            self.user.save()
        return response

class KakaoLoginView(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
    callback_url = settings.KAKAO_CALLBACK_URL
    client_class = OAuth2Client

    def get_response(self):
        response = super().get_response()
        if self.user:
            self.user.provider = 'kakao'
            self.user.save()
        return response

class NaverLoginView(SocialLoginView):
    adapter_class = NaverOAuth2Adapter
    callback_url = settings.NAVER_CALLBACK_URL
    client_class = OAuth2Client

    def get_response(self):
        response = super().get_response()
        if self.user:
            self.user.provider = 'naver'
            self.user.save()
        return response

class ObtainSocialJWT(APIView):
    """소셜 로그인 후 JWT 발급"""
    def post(self, request):
        user = request.user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'provider': user.provider
            }
        }, status=status.HTTP_200_OK)

class SocialLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        provider = request.data.get('provider')
        access_token = request.data.get('access_token')

        if not all([provider, access_token]):
            return Response({
                'error': '제공자와 액세스 토큰이 필요합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 소셜 로그인 처리 로직
            user_data = self.get_social_user_data(provider, access_token)
            user = self.get_or_create_user(provider, user_data)
            
            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'provider': user.provider
                }
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def get_social_user_data(self, provider, access_token):
        # 각 소셜 제공자별 사용자 정보 조회 로직
        if provider == 'google':
            return self.get_google_user_data(access_token)
        elif provider == 'naver':
            return self.get_naver_user_data(access_token)
        elif provider == 'kakao':
            return self.get_kakao_user_data(access_token)
        raise ValueError('지원하지 않는 소셜 제공자입니다.')