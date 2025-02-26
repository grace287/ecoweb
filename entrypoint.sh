#!/bin/bash

# Gunicorn을 여러 포트에서 실행
gunicorn config.wsgi:application --bind 0.0.0.0:8000 &
gunicorn config.wsgi:application --bind 0.0.0.0:8001 &
gunicorn config.wsgi:application --bind 0.0.0.0:8002 &
gunicorn config.wsgi:application --bind 0.0.0.0:8003 &

# 실행 중인 프로세스 유지
wait -n
