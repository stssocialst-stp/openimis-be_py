#!/bin/bash
set -e

show_help() {
  echo """
Commands
---------------------------------------------------------------
start            : start django (gunicorn)
worker           : start Celery worker
start_asgi       : start Django ASGI (daphne)
manage           : run django manage.py
eval             : eval shell command
bash             : run bash
"""
}

init(){
  if [ "${DJANGO_MIGRATE,,}" == "true" ]; then
    echo "Migrating..."
    python manage.py migrate
  fi
}

start_wsgi() {
  init
  echo "Starting Django WSGI with Gunicorn..."

  SERVER_IP="${WSGI_IP:-0.0.0.0}"
  SERVER_PORT="${WSGI_PORT:-8000}"
  SERVER_APPLICATION="${WSGI_APPLICATION:-openIMIS.wsgi}"
  SERVER_WORKERS="${WSGI_WORKERS:-1}"

  exec gunicorn \
    -b "$SERVER_IP:$SERVER_PORT" \
    -w "$SERVER_WORKERS" \
    --timeout 120 \
    --graceful-timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    "$SERVER_APPLICATION"
}

if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
  export DJANGO_SETTINGS_MODULE=openIMIS.settings
fi

case "$1" in
  start | start_wsgi)
    start_wsgi
  ;;
  start_asgi)
    init
    daphne -b "${ASGI_IP:-0.0.0.0}" -p "${ASGI_PORT:-8000}" "${ASGI_APPLICATION:-openIMIS.asgi:application}"
  ;;
  worker)
    echo "Starting Celery worker..."
    celery -A openIMIS worker --loglevel=INFO
  ;;
  manage)
    ./manage.py "${@:2}"
  ;;
  eval)
    eval "${@:2}"
  ;;
  bash)
    bash
  ;;
  *)
    show_help
  ;;
esac
