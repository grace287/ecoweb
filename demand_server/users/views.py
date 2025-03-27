from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import redirect, render
from users.serializers import SignupSerializer, LoginSerializer, ProfileSerializer, PasswordChangeSerializer
from users.models import DemandUser
from drf_spectacular.utils import extend_schema


class SignupView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
    request=SignupSerializer,
    responses={201: {"success": True, "redirect_url": "/signup/success/"}},
    tags=["Authentication"],
    summary="회원가입 API",
    description="신규 사용자를 등록하고 자동으로 승인/활성화된 상태로 저장합니다."
)
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "redirect_url": "/signup/success/"}, status=201)
        return Response({"success": False, "errors": serializer.errors}, status=400)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            auth_login(request, user)
            request.session.set_expiry(0)
            request.session.modified = True
            return Response({"success": True, "redirect_url": "/main"}, status=200)
        return Response({"success": False, "errors": serializer.errors}, status=400)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        auth_logout(request)
        return redirect("main")


class SignupSuccessView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, "accounts/signup_success.html")


class CheckUsernameDuplicateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        if not username:
            return Response({"success": False, "error": "아이디를 입력해주세요."}, status=400)
        is_duplicate = DemandUser.objects.filter(username=username).exists()
        return Response({"success": True, "is_duplicate": is_duplicate})


class CheckEmailDuplicateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"success": False, "error": "이메일을 입력해주세요."}, status=400)
        is_duplicate = DemandUser.objects.filter(email=email).exists()
        return Response({"success": True, "is_duplicate": is_duplicate})


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "정보가 수정되었습니다."})
        return Response({"success": False, "errors": serializer.errors}, status=400)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "정보가 수정되었습니다."})
        return Response({"success": False, "errors": serializer.errors}, status=400)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"success": False, "error": "기존 비밀번호가 일치하지 않습니다."}, status=400)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"success": True, "message": "비밀번호가 변경되었습니다."})
        return Response({"success": False, "errors": serializer.errors}, status=400)
    

class CustomizationUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        region = request.data.get('region')
        industry = request.data.get('industry')

        profile = request.user.profile
        profile.region = region
        profile.industry = industry
        profile.save()

        return Response({"success": True, "message": "맞춤 설정이 저장되었습니다."}, status=200)