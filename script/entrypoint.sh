#!/bin/bash
set -e

show_help() {
  echo """
  Commands
  ---------------------------------------------------------------

  start            : start django
  worker           : start Celery worker
  start_asgi       : use daphne -b ASGI_IP:WSGI_PORT -p SERVER_PORT  ASGI_APPLICATION
  start_wsgi       : use gunicorn -b WSGI_IP:WSGI_PORT -w WSGI_WORKERS WSGI_APPLICATION
  manage           : run django manage.py
  eval             : eval shell command
  bash             : run bash
  """
}

init(){
  # Install PEP+ module if it exists (for development)
  if [ -d "/app/openimis-be-pep_plus_py" ]; then
    echo "Installing PEP+ module..."
    pip install -e /app/openimis-be-pep_plus_py

    # Add pep_plus to openimis config if not already there
    CONF_FILE="${OPENIMIS_CONF_JSON:-/openimis-be/openimis.json}"
    echo "Adding pep_plus to $CONF_FILE..."
    python3 << EOF
import json
import sys

conf_file = "$CONF_FILE"
try:
    with open(conf_file, 'r') as f:
        config = json.load(f)

    # Check if pep_plus already exists
    module_names = [m['name'] for m in config.get('modules', [])]
    if 'pep_plus' not in module_names:
        # Find position before signal_binding (which should be last)
        insert_pos = len(config['modules'])
        config['modules'].insert(insert_pos, {
            "name": "pep_plus",
            "pip": "-e /app/openimis-be-pep_plus_py"
        })

        with open(conf_file, 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ pep_plus added to configuration")
    else:
        print("ℹ️ pep_plus already in configuration")
except Exception as e:
    print(f"⚠️ Could not modify config: {e}")
    sys.exit(0)  # Continue anyway
EOF
  fi

  # Run migrations FIRST (before Django apps initialize)
  if [ "${DJANGO_MIGRATE,,}" == "true" ] || [ "${SCHEDULER_AUTOSTART,,}" == "false" ]; then
        echo "Running migrations (standalone mode to avoid scheduler)..."
        python /openimis-be/script/run_migrations.py || {
          echo "⚠️ Standalone migration failed, trying standard migration..."
          python manage.py migrate --noinput
        }
        echo "Migrations completed. Scheduler will start on next restart."
        export SCHEDULER_AUTOSTART=True
  fi

  # Compile messages and collect static files (moved from Dockerfile)
  if [ ! -f /openimis-be/.init_done ]; then
    echo "Compiling messages..."
    python manage.py compilemessages -x zh_Hans || echo "Warning: compilemessages failed"
    echo "Collecting static files..."
    python manage.py collectstatic --clear --noinput || echo "Warning: collectstatic failed"
    touch /openimis-be/.init_done
  fi
}

#export PYTHONPATH="/opt/app:$PYTHONPATH"
if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
  export DJANGO_SETTINGS_MODULE=openIMIS.settings
fi

case "$1" in
  "start" )
    init
    echo "Starting Django..."
    python server.py
  ;;
  "start_asgi" )
    init
    echo "Starting Django ASGI..."
    def_ip='0.0.0.0'
    def_port='8000'
    def_app='openIMIS.asgi:application'

    SERVER_IP="${ASGI_IP:-$def_ip}"
    SERVER_PORT="${ASGI_PORT:-$def_port}"
    SERVER_APPLICATION="${ASGI_APPLICATION:-$def_app}"

    daphne -b "$SERVER_IP" -p "$SERVER_PORT" "$SERVER_APPLICATION"
  ;;
  "start_wsgi" )
    init
    echo "Starting Django WSGI..."
    def_ip='0.0.0.0'
    def_port='8000'
    def_app='openIMIS.wsgi'

    SERVER_IP="${WSGI_IP:-$def_ip}"
    SERVER_PORT="${WSGI_PORT:-$def_port}"
    SERVER_APPLICATION="${WSGI_APPLICATION:-$def_app}"
    SERVER_WORKERS="${WSGI_WORKERS:-4}"

    gunicorn -b "$SERVER_IP:$SERVER_PORT" -w $SERVER_WORKERS "$SERVER_APPLICATION"
  ;;
  "worker" )
    echo "Starting Celery with url ${CELERY_BROKER_URL} ${DB_NAME}..."
    echo "Settings module: $DJANGO_SETTINGS_MODULE"
    celery -A openIMIS worker --loglevel=DEBUG
  ;;
  "manage" )
    ./manage.py "${@:2}"
  ;;
  "eval" )
    eval "${@:2}"
  ;;
  "bash" )
    bash
  ;;
  * )
    show_help
  ;;
esac
