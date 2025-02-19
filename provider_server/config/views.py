from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login as auth_login
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from users.models import CustomUser, ServiceCategory, Attachment  # 올바른 경로로 수정
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def main(request):
    return render(request, 'main.html') 

def provider_login(request):
    return render(request, 'accounts/provider_login.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        # AJAX 요청 여부 확인
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if user is not None:
            if user.is_approved:
                auth_login(request, user)
                return JsonResponse({
                    'success': True,
                    'redirect_url': '/dashboard/'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': '관리자의 승인이 필요합니다.'
                })
        else:
            return JsonResponse({
                'success': False,
                'error': '아이디 또는 비밀번호가 잘못되었습니다.'
            })

    return render(request, 'accounts/provider_login.html')

@login_required
@csrf_exempt
def provider_logout(request):
    return redirect('provider_login')

@csrf_exempt
def provider_signup(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            company_name = request.POST.get('company_name')
            business_registration_number = request.POST.get('business_registration_number')
            business_phone_number = request.POST.get('business_phone_number')
            consulting_phone_number = request.POST.get('consulting_phone_number')
            address = request.POST.get('address')
            address_detail = request.POST.get('address_detail')
            service_category = request.POST.get('service_category')
            attachments = request.FILES.getlist('attachment')

            # 기본 유효성 검사
            if not all([username, email, password, company_name, 
                       business_registration_number, business_phone_number, address]):
                return render(request, 'accounts/provider_signup.html', {
                    'error': '필수 항목을 모두 입력해주세요.',
                    'service_categories': ServiceCategory.objects.all()
                })

            # 중복 체크
            if CustomUser.objects.filter(username=username).exists():
                return render(request, 'accounts/provider_signup.html', {
                    'error': '이미 사용 중인 아이디입니다.',
                    'service_categories': ServiceCategory.objects.all()
                })

            if CustomUser.objects.filter(email=email).exists():
                return render(request, 'accounts/provider_signup.html', {
                    'error': '이미 사용 중인 이메일입니다.',
                    'service_categories': ServiceCategory.objects.all()
                })

            if CustomUser.objects.filter(business_registration_number=business_registration_number).exists():
                return render(request, 'accounts/provider_signup.html', {
                    'error': '이미 등록된 사업자등록번호입니다.',
                    'service_categories': ServiceCategory.objects.all()
                })

            # 사용자 생성
            user = CustomUser(
                username=username,
                email=email,
                password=make_password(password),
                company_name=company_name,
                business_registration_number=business_registration_number,
                business_phone_number=business_phone_number,
                consultation_phone_number=consulting_phone_number,
                address=address,
                address_detail=address_detail,
            )
            user.save()

            # 서비스 카테고리 설정
            if service_category:
                category_codes = service_category.split(',')
                categories = ServiceCategory.objects.filter(category_code__in=category_codes)
                user.service_category.set(categories)

            # 첨부파일 저장
            for attachment in attachments:
                Attachment.objects.create(user=user, file=attachment)

            return redirect('provider_signup_pending')

        except Exception as e:
            return render(request, 'accounts/provider_signup.html', {
                'error': str(e),
                'service_categories': ServiceCategory.objects.all()
            })

    else:
        return render(request, 'accounts/provider_signup.html', {
            'service_categories': ServiceCategory.objects.all()
        })

def signup(request):
    return render(request, 'accounts/provider_signup.html')

def provider_signup_pending(request):
    return render(request, 'accounts/provider_signup_pending.html')

@csrf_exempt
def check_id_duplicate(request):
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
def verify_business_number(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            business_number = data.get("business_number")

            if not business_number:
                return JsonResponse({"error": "사업자등록번호를 입력해주세요."}, status=400)

            # 사업자등록번호 검증 로직 추가
            # 예시: 사업자등록번호 검증 API 호출
            is_valid = True  # 검증 결과 예시

            return JsonResponse({"is_valid": is_valid})

        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 데이터 형식입니다."}, status=400)

    return JsonResponse({"error": "잘못된 요청"}, status=400)


@login_required
def provider_dashboard(request):
    return render(request, 'provider/provider_dashboard.html')

@login_required
def provider_profile(request):
    if not request.user.is_authenticated:
        return redirect('provider_login')
        
    context = {
        'user': request.user,
        'service_categories': request.user.service_category.all(),
    }
    return render(request, 'accounts/provider_profile.html', context)

