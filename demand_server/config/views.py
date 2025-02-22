from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login as auth_login, logout as auth_logut
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from users.models import CustomUser
from django.views.decorators.csrf import csrf_exempt
import json


def landing(request):
    return render(request, "landing.html")

def main(request):
    return render(request, "main.html")

@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 사용자 인증
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/main'})
        else:
            return JsonResponse({'success': False, 'error': '아이디 또는 비밀번호가 올바르지 않습니다.'}, status=400)

    return render(request, "accounts/login_modal.html")

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        company_name = request.POST.get('company_name')
        business_phone_number = request.POST.get('business_phone_number')
        address = request.POST.get('address')
        address_detail = request.POST.get('address_detail')
        recommend_id = request.POST.get('recommend_id')

        if not username:
            return JsonResponse({'success': False, 'error': '아이디를 입력해주세요.'})
        if not email:
            return JsonResponse({'success': False, 'error': '이메일을 입력해주세요.'})
        if not password:
            return JsonResponse({'success': False, 'error': '비밀번호를 입력해주세요.'})
        if not company_name:
            return JsonResponse({'success': False, 'error': '업체명을 입력해주세요.'})
        if not business_phone_number:
            return JsonResponse({'success': False, 'error': '담당자 휴대폰 번호를 입력해주세요.'})
        if not address:
            return JsonResponse({'success': False, 'error': '주소를 입력해주세요.'})

        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': '이미 사용 중인 아이디입니다.'})
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': '이미 사용 중인 이메일입니다.'})

        # 사용자 생성 (비밀번호 해싱)
        user = CustomUser(
            username=username,
            email=email,
            password=make_password(),
            company_name=company_name,
            business_phone_number=business_phone_number,
            address=address,
            address_detail=address_detail,
            recommend_id=recommend_id
        )
        user.save()
        auth_login(request, user)  # 로그인 처리
        return JsonResponse({'success': True, 'redirect_url': '/signup_success/'})
    return render(request, "accounts/signup.html")

def signup_success(request):
    return render(request, "accounts/signup_success.html")

@csrf_exempt
def check_id_duplicate(request):
    """아이디 중복 확인 API"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("id")

            if not user_id:
                return JsonResponse({"error": "아이디를 입력해주세요."}, status=400)

            is_duplicate = CustomUser.objects.filter(username=user_id).exists()
            return JsonResponse({"is_duplicate": is_duplicate})

        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 데이터 형식입니다."}, status=400)

    return JsonResponse({"error": "잘못된 요청"}, status=400)

@csrf_exempt
def check_email_duplicate(request):
    """이메일 중복 확인 API"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if not email:
                return JsonResponse({"error": "이메일을 입력해주세요."}, status=400)

            is_duplicate = CustomUser.objects.filter(email=email).exists()
            return JsonResponse({"is_duplicate": is_duplicate})

        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 데이터 형식입니다."}, status=400)

    return JsonResponse({"error": "잘못된 요청"}, status=400)


def profile(request):
    return render(request, "accounts/profile.html")

def logout(request):
    auth_logut(request)
    return redirect('main')


