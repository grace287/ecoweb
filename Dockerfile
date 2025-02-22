FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 시스템 패키지 설치 (필요한 경우 추가)
RUN apt-get update && apt-get install -y build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

# 의존성 설치
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# 소스 복사
COPY . /app/

# Gunicorn 서버 실행
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]