from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return HttpResponse("""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Common API Server</title>
        </head>
        <body>
            <h1>common_api_server</h1>
            <p>결제 api server 입니다. 포트 : 8004</p>
            <p>공통 api 호출 앱 : payment</p>
        </body>
        </html>
    """)
