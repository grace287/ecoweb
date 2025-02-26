FROM python:3.12-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 시스템 패키지 설치 (MySQL 개발 라이브러리 추가)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    pkg-config \
    curl && \
    rm -rf /var/lib/apt/lists/*
# 의존성 설치
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# 소스 코드 복사
COPY . /app/

# 엔트리포인트 스크립트 복사
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# 실행 명령
ENTRYPOINT ["/app/entrypoint.sh"]
