from django.urls import path

urlpatterns = [
    path('request/guest/', estimate_request_guest, name='estimate_request_guest'),  # 비회원용
    path('request/form/', estimate_request_form, name='request_form'),  # 회원용
    path('request/submit/', estimate_request_submit, name='request_submit'),  # 견적 제출
    path("success/", estimate_success, name="estimate_success"),  # 견적 요청 성공 페이지
]